#!/usr/bin/env bash
#
# provision-cloudkitty.sh
#
# Stands up a CloudKitty serving host from a fresh Ubuntu 24.04 box:
#   read-only GitHub deploy key -> clone -> Rust toolchain -> build ->
#   /opt/cloudkitty + cloudkitty user -> systemd unit -> Caddy -> ufw -> hardening
#
# One world per server. The proxy target is read out of the installed
# cloudkitty.toml rather than configured here, so the two cannot disagree; the
# config file itself is never modified.
#
# Fresh-box only. It is NOT idempotent: it assumes nothing here exists yet and
# will happily clobber config it did not write. Run it once, on a new droplet.
#
# Services are installed and ENABLED but NOT STARTED, so you control the first
# boot of the world (snapshot placement, cert issuance). The script prints the
# start commands when it finishes.
#
# Usage:
#   sudo bash provision-cloudkitty.sh
#
# Exit codes:
#   0  provisioned
#   1  failed
#   3  stopped deliberately: a deploy key was generated and needs registering
#      in GitHub before a second run can continue
#
# Every setting below can be overridden from the environment, e.g.
#   sudo CK_SWAP=0 CK_FAIL2BAN=1 bash provision-cloudkitty.sh

set -euo pipefail

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

# --- identity / source -----------------------------------------------------
CK_REPO="${CK_REPO:-CloudKitty-ai/cloudkitty}"
CK_BRANCH="${CK_BRANCH:-main}"
CK_BUILD_DIR="${CK_BUILD_DIR:-/root/cloudkitty}"     # where root builds
CK_APP_DIR="${CK_APP_DIR:-/opt/cloudkitty}"          # what the service runs
CK_STATE_DIR="${CK_STATE_DIR:-${CK_APP_DIR}/state}"  # the ONLY writable path
CK_USER="${CK_USER:-cloudkitty}"
CK_DEPLOY_KEY="${CK_DEPLOY_KEY:-/root/.ssh/cloudkitty-server}"

# --- public face -----------------------------------------------------------
# Both domains are served by one site block; the www variants redirect to them.
# There is deliberately no port knob: the port comes from `bind` in the
# installed cloudkitty.toml (see "Proxy target" in step 7).
#
# kitties.ai leads because it is the canonical host: client/index.html hardcodes
# it in og:url and og:image, and the first name here is the one this script
# echoes in its DNS instructions. See the Hostnames section of
# docs/deployment.md.
CK_DOMAINS="${CK_DOMAINS:-kitties.ai cloudkitty.ai}"

# --- toggles (see the accompanying notes for the reasoning) ----------------
CK_SWAP="${CK_SWAP:-1}"                  # 2G swapfile + swappiness=10
CK_SWAP_SIZE="${CK_SWAP_SIZE:-2G}"
CK_HARDEN_UNIT="${CK_HARDEN_UNIT:-1}"    # systemd sandboxing on cloudkitty.service
CK_MEMORY_MAX="${CK_MEMORY_MAX:-2G}"     # only applied when CK_HARDEN_UNIT=1
CK_HARDEN_SSH="${CK_HARDEN_SSH:-1}"      # password auth off (guarded)
CK_UNATTENDED="${CK_UNATTENDED:-1}"      # security updates, no auto-reboot
CK_JOURNAL_CAP="${CK_JOURNAL_CAP:-1}"    # cap journald at 200M
CK_FAIL2BAN="${CK_FAIL2BAN:-0}"          # sshd jail
CK_MAKE_ARTIFACT_DIR="${CK_MAKE_ARTIFACT_DIR:-1}"  # mkdir an scp target for any
                                                   # artifact not committed to policies/
CK_START_SERVICES="${CK_START_SERVICES:-0}"        # 1 = start cloudkitty + caddy at the end

# GitHub's published ed25519 host key fingerprint, so the clone is not
# trust-on-first-use. https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/githubs-ssh-key-fingerprints
GITHUB_ED25519_FP="SHA256:+DiY3wvvV6TuJJhbpZisF/zLDA0zPMSvHdkr4UvCOqU"

# Caddy's apt signing key, pinned for the same reason: an apt signing key is
# permanent root-level trust, re-used by every unattended-upgrades run.
#
# This is the PRIMARY key fingerprint (rsa4096, created 2016-04-01, uid
# "Caddy Web Server <contact@caddyserver.com>"), deliberately not a subkey:
# Caddy's signing subkeys have expired and rotated before (caddyserver/caddy
# #7411), and the primary fingerprint is stable across that.
# Verify independently at https://cloudsmith.io/~caddy/repos/stable/pub-keys/
# before changing this value.
CADDY_GPG_FP="65760C51EDEA2017CEA2CA15155B6D79CA56EA34"

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

step() { printf '\n\033[1;36m==> %s\033[0m\n' "$*"; }
info() { printf '    %s\n' "$*"; }
warn() { printf '\033[1;33m    warning: %s\033[0m\n' "$*"; }
die()  { printf '\033[1;31m    error: %s\033[0m\n' "$*" >&2; exit 1; }

# ---------------------------------------------------------------------------
# 0. Preflight
# ---------------------------------------------------------------------------

step "Preflight"

[[ $EUID -eq 0 ]] || die "run as root (sudo bash $0)"

# mapfile, and empty-array expansion under `set -u`, both need bash >= 4.4.
# Ubuntu 24.04 ships 5.2; macOS ships 3.2, where this would fail in confusing
# ways several hundred lines in rather than being refused here.
if (( BASH_VERSINFO[0] < 4 || (BASH_VERSINFO[0] == 4 && BASH_VERSINFO[1] < 4) )); then
    die "bash >= 4.4 required (found ${BASH_VERSION}); this script targets Ubuntu 24.04"
fi

if [[ -r /etc/os-release ]]; then
    # shellcheck source=/dev/null
    . /etc/os-release
    [[ "${ID:-}" == "ubuntu" ]] || warn "built for Ubuntu; found ID=${ID:-unknown}"
    [[ "${VERSION_ID:-}" == "24.04" ]] || warn "built for Ubuntu 24.04; found ${VERSION_ID:-unknown}"
fi

# Fresh-box guard: refuse to run over an existing install.
for path in "$CK_APP_DIR" "$CK_BUILD_DIR" /etc/systemd/system/cloudkitty.service; do
    if [[ -e "$path" ]]; then
        die "$path already exists — this script is fresh-box only.

    If a PREVIOUS RUN FAILED PART-WAY, remove what it created and re-run:

      systemctl disable --now cloudkitty caddy 2>/dev/null || true
      rm -f  /etc/systemd/system/cloudkitty.service
      rm -rf ${CK_BUILD_DIR}
      rm -rf ${CK_APP_DIR}

    ** Check ${CK_STATE_DIR}/snapshot.json first. ** That file is the world,
    and the line above deletes it. If a world has ever been placed here, copy
    it somewhere safe before removing anything:

      cp -a ${CK_STATE_DIR}/snapshot.json /root/snapshot.json.rescued

    If this box is already SERVING, none of the above applies — you want
    /root/update.sh, not this script."
    fi
done

# Normalize the domain list once, here, so stray whitespace in CK_DOMAINS
# cannot reach the Caddyfile as an empty site address.
read -ra CK_DOMAIN_LIST <<< "$CK_DOMAINS"
[[ ${#CK_DOMAIN_LIST[@]} -gt 0 ]] || die "CK_DOMAINS is empty"

# Local kernel query, no packets sent — used only for the closing instructions.
PUBLIC_ADDR="$(ip -4 route get 1.1.1.1 2>/dev/null \
    | awk '{for (i = 1; i <= NF; i++) if ($i == "src") { print $(i+1); exit }}' || true)"
[[ -n "$PUBLIC_ADDR" ]] || PUBLIC_ADDR="${CK_DOMAIN_LIST[0]}"

info "Ubuntu ${VERSION_ID:-?}, $(nproc) vCPU, $(free -h | awk '/^Mem:/{print $2}') RAM"
info "repo:    git@github.com:${CK_REPO}.git (${CK_BRANCH})"
info "domains: ${CK_DOMAIN_LIST[*]}"
info "address: ${PUBLIC_ADDR}"

# ---------------------------------------------------------------------------
# 1. Deploy key
# ---------------------------------------------------------------------------
#
# Read-only key, this host only. If it is not here yet we generate one, print
# the public half, and stop — nothing else has been touched at this point, so
# re-running after you register it in GitHub is clean.

step "GitHub deploy key"

install -d -m 700 /root/.ssh

if [[ ! -f "$CK_DEPLOY_KEY" ]]; then
    ssh-keygen -t ed25519 -N '' -C "cloudkitty-deploy@$(hostname)" -f "$CK_DEPLOY_KEY" >/dev/null
    chmod 600 "$CK_DEPLOY_KEY"
    cat <<EOF

    A new deploy key was generated. Add its public half to the repository:

      https://github.com/${CK_REPO}/settings/keys/new
      Title: $(hostname)
      Key:   (below)
      [ ] Allow write access   <- leave UNCHECKED, this key only pulls

$(cat "${CK_DEPLOY_KEY}.pub")

    Then re-run this script. Nothing else has been modified.

EOF
    # Exit 3, not 0: a caller (cloud-init, Terraform, CI) must be able to tell
    # "waiting on a human" apart from "provisioned".
    exit 3
fi

info "using existing key $CK_DEPLOY_KEY"
chmod 600 "$CK_DEPLOY_KEY"

# Pin github.com's host key rather than accepting whatever answers first.
if ! grep -q '^github\.com ' /root/.ssh/known_hosts 2>/dev/null; then
    # Assign and test separately: a bare `x="$(cmd)"` under set -e aborts the
    # script on failure, so the diagnostic below would never print.
    scanned="$(ssh-keyscan -t ed25519 github.com 2>/dev/null || true)"
    [[ -n "$scanned" ]] || die "could not reach github.com to fetch its host key"
    # Same assign-then-test discipline as above: a garbled keyscan response
    # makes ssh-keygen fail, and a bare assignment would abort the script with
    # no message instead of reaching the fingerprint-mismatch die below.
    got="$(printf '%s\n' "$scanned" | ssh-keygen -lf - 2>/dev/null | awk '{print $2}' || true)"
    [[ -n "$got" ]] || die "could not read a host key fingerprint from github.com's response"
    [[ "$got" == "$GITHUB_ED25519_FP" ]] \
        || die "github.com host key fingerprint mismatch: got $got, expected $GITHUB_ED25519_FP"
    printf '%s\n' "$scanned" >> /root/.ssh/known_hosts
    info "pinned github.com host key ($got)"
fi

# Make plain `git pull` in the checkout use this key and only this key.
touch /root/.ssh/config
chmod 600 /root/.ssh/config
if ! grep -q '^Host github\.com$' /root/.ssh/config; then
    cat >> /root/.ssh/config <<EOF

Host github.com
    HostName github.com
    User git
    IdentityFile ${CK_DEPLOY_KEY}
    IdentitiesOnly yes
EOF
fi

# ---------------------------------------------------------------------------
# 2. Base packages
# ---------------------------------------------------------------------------

step "Base packages"

export DEBIAN_FRONTEND=noninteractive
apt-get update -qq
apt-get upgrade -y -qq

# build-essential + pkg-config + libssl-dev cover the native crates in the
# lockfile (cc, ring, openssl-sys). python3-dev is deliberately absent: the
# build is scoped with -p cloudkitty-server, so cloudkitty-py never compiles.
apt-get install -y -qq \
    build-essential pkg-config libssl-dev \
    git curl ca-certificates gnupg rsync \
    debian-keyring debian-archive-keyring apt-transport-https \
    ufw

# ---------------------------------------------------------------------------
# 3. Swap
# ---------------------------------------------------------------------------

if [[ "$CK_SWAP" == "1" ]]; then
    step "Swap (${CK_SWAP_SIZE})"
    # Not `swapon --show | grep -q`: that pipeline returns SIGPIPE under
    # pipefail whenever grep wins the race (see the caddy repo check, step 10).
    if [[ -n "$(swapon --show --noheadings)" ]]; then
        info "swap already active, skipping"
    else
        fallocate -l "$CK_SWAP_SIZE" /swapfile
        chmod 600 /swapfile
        mkswap /swapfile >/dev/null
        swapon /swapfile
        grep -q '^/swapfile ' /etc/fstab || echo '/swapfile none swap sw 0 0' >> /etc/fstab
        printf 'vm.swappiness=10\n' > /etc/sysctl.d/99-cloudkitty-swappiness.conf
        sysctl -q --system
        info "$(free -h | awk '/^Swap:/{print $2}') swap online, swappiness=10"
    fi
fi

# ---------------------------------------------------------------------------
# 4. Service account
# ---------------------------------------------------------------------------

step "User: ${CK_USER}"

if id -u "$CK_USER" >/dev/null 2>&1; then
    info "already exists"
else
    # System account: no login shell, no password, home is the app dir itself.
    useradd --system --user-group --home-dir "$CK_APP_DIR" --shell /usr/sbin/nologin "$CK_USER"
    info "created (uid $(id -u "$CK_USER"), nologin)"
fi

install -d -o "$CK_USER" -g "$CK_USER" -m 755 "$CK_APP_DIR"

# ---------------------------------------------------------------------------
# 5. Rust toolchain (root builds)
# ---------------------------------------------------------------------------

step "Rust toolchain"

# Pin the install location instead of inheriting $HOME: run via `su` without a
# login shell and rustup would install somewhere the lookups below never check.
export CARGO_HOME=/root/.cargo
export RUSTUP_HOME=/root/.rustup

if [[ -x "${CARGO_HOME}/bin/cargo" ]]; then
    info "already installed: $("${CARGO_HOME}/bin/rustc" --version)"
else
    curl -sSf https://sh.rustup.rs | sh -s -- -y --profile minimal --default-toolchain stable
    [[ -x "${CARGO_HOME}/bin/cargo" ]] || die "rustup did not install cargo into ${CARGO_HOME}"
    info "installed: $("${CARGO_HOME}/bin/rustc" --version)"
fi
export PATH="${CARGO_HOME}/bin:$PATH"

# ---------------------------------------------------------------------------
# 6. Clone and build
# ---------------------------------------------------------------------------

step "Clone ${CK_REPO}"

git clone --branch "$CK_BRANCH" "git@github.com:${CK_REPO}.git" "$CK_BUILD_DIR"
info "cloned to $CK_BUILD_DIR at $(git -C "$CK_BUILD_DIR" rev-parse --short HEAD)"

step "Build (release)"

# -p cloudkitty-server matters: a bare `cargo build` also compiles
# cloudkitty-py, which links the Python dev libraries a serving box has no
# reason to carry. See docs/deployment.md.
( cd "$CK_BUILD_DIR" && cargo build --release -p cloudkitty-server )

BIN="${CK_BUILD_DIR}/target/release/cloudkitty-server"
[[ -x "$BIN" ]] || die "build produced no binary at $BIN"
info "built $(du -h "$BIN" | cut -f1) binary"

# ---------------------------------------------------------------------------
# 7. Install into /opt/cloudkitty
# ---------------------------------------------------------------------------

step "Install to ${CK_APP_DIR}"

# Everything the service READS is root-owned; only the state directory is
# writable by it. The service previously owned its own executable inside
# ReadWritePaths, so any write-primitive bug in the server could replace the
# binary and Restart=on-failure would re-execute it -- defeating the whole
# sandbox below. Root-owned code plus a narrow writable state dir closes that.
install -o root -g root -m 755 "$BIN" "${CK_APP_DIR}/cloudkitty-server"
install -o root -g root -m 644 "${CK_BUILD_DIR}/cloudkitty.toml" "${CK_APP_DIR}/cloudkitty.toml"
rsync -a --delete "${CK_BUILD_DIR}/client/" "${CK_APP_DIR}/client/"
# The deployed policy artifacts are committed to policies/ (owner decision
# 2026-07-31, policies/README.md), so they arrive with the clone and deploy
# exactly like the viewer -- same --delete, for the same reason: a retired
# .ckpolicy left behind is one the config could still name.
if [[ -d "${CK_BUILD_DIR}/policies" ]]; then
    rsync -a --delete "${CK_BUILD_DIR}/policies/" "${CK_APP_DIR}/policies/"
fi
chown -R root:root "${CK_APP_DIR}/client"
if [[ -d "${CK_APP_DIR}/policies" ]]; then
    chown -R root:root "${CK_APP_DIR}/policies"
fi

# The world lives here and nowhere else -- the only path the service can write.
# ExecStart passes --snapshot, which overrides [persistence].snapshot_path
# (main.rs), so cloudkitty.toml is still never modified by this script.
install -d -o "$CK_USER" -g "$CK_USER" -m 750 "${CK_STATE_DIR}"

# --- Proxy target ----------------------------------------------------------
# One world per server, so the config is the single source of truth for the
# port: read it here and hand it to Caddy, rather than carrying a knob that can
# silently disagree with the file. The config itself is never modified.
# Accept both TOML string forms. `bind` is #[serde(default)] in the engine
# (config/defaults.rs::default_bind), so a config that omits it is valid and
# runs on 127.0.0.1:8090 -- dying here would refuse a config the server
# accepts, after /opt/cloudkitty already exists.
CK_BIND="$(grep -oP '^\s*bind\s*=\s*["'"'"']\K[^"'"'"']+' "${CK_APP_DIR}/cloudkitty.toml" | head -n1 || true)"
if [[ -z "$CK_BIND" ]]; then
    CK_BIND="127.0.0.1:8090"
    info "no bind = in cloudkitty.toml; using the engine default ${CK_BIND}"
fi

# Split host from port, keeping bracketed IPv6 literals intact.
case "$CK_BIND" in
    \[*\]:*) CK_BIND_HOST="${CK_BIND%]:*}]"; CK_BIND_PORT="${CK_BIND##*:}" ;;
    *:*)     CK_BIND_HOST="${CK_BIND%:*}";   CK_BIND_PORT="${CK_BIND##*:}" ;;
    *)       die "cannot parse bind = \"${CK_BIND}\" as host:port" ;;
esac

case "$CK_BIND_HOST" in
    127.0.0.1|localhost|'[::1]') ;;
    *) die "cloudkitty.toml binds ${CK_BIND}, not loopback — the server would be publicly reachable, bypassing Caddy" ;;
esac

# Carry the host through to reverse_proxy rather than assuming IPv4. A config
# binding [::1] used to provision cleanly and then 502 on every request,
# because Caddy was pointed at 127.0.0.1 where nothing was listening.
CK_PROXY_UPSTREAM="${CK_BIND_HOST}:${CK_BIND_PORT}"
info "proxy target ${CK_PROXY_UPSTREAM} (from cloudkitty.toml)"

# The RL policy artifacts the config expects; read once, checked again in the
# closing summary. Anything under policies/ landed in the rsync above. A config
# may still name an artifact from outside the tree (experiments/**/artifacts/
# is gitignored), and only that kind still needs an scp target made for it.
#
# Only policies a kitty actually names are required: the server collects
# `behavior = "policy:<name>"` across the roster and loads just those
# (cloudkitty-server/src/lib.rs). An [rl.policy.*] block no kitty references is
# never opened, so demanding its artifact would send the operator chasing a
# file the server will never look for.
mapfile -t CK_POLICY_NAMES < <(grep -oP '^\s*behavior\s*=\s*["'"'"']policy:\K[^"'"'"']+' "${CK_APP_DIR}/cloudkitty.toml" || true)

CK_ARTIFACTS=()
for name in "${CK_POLICY_NAMES[@]}"; do
    # The artifact line belonging to [rl.policy.<name>]: take the first
    # `artifact =` after that section header.
    # Three separate subs, not one alternation: POSIX awk matches
    # leftmost-LONGEST, so /^["']|["'].*$/ matches the whole value from its
    # opening quote and erases it. Verified against the real cloudkitty.toml.
    art="$(awk -v want="[rl.policy.${name}]" '
        $0 ~ /^\[/ { insec = ($0 == want) }
        insec && /^[ \t]*artifact[ \t]*=/ {
            sub(/^[^=]*=[ \t]*/, "")
            sub(/^["'"'"']/, "")
            sub(/["'"'"'].*$/, "")
            print
            exit
        }' "${CK_APP_DIR}/cloudkitty.toml" || true)"
    [[ -n "$art" ]] || die "a kitty names behavior \"policy:${name}\" but cloudkitty.toml has no [rl.policy.${name}] artifact — the server refuses to start on this"
    CK_ARTIFACTS+=("$art")
done

CK_ARTIFACTS_PRESENT=0
for rel in "${CK_ARTIFACTS[@]}"; do
    # Absolute paths are used verbatim by the server, so they must not be
    # reinterpreted as relative to the app dir.
    case "$rel" in
        /*) target="$rel" ;;
        *)  target="${CK_APP_DIR}/${rel}" ;;
    esac
    if [[ -f "$target" ]]; then
        CK_ARTIFACTS_PRESENT=$((CK_ARTIFACTS_PRESENT + 1))
    elif [[ "$CK_MAKE_ARTIFACT_DIR" == "1" ]]; then
        install -d -o "$CK_USER" -g "$CK_USER" -m 755 "$(dirname "$target")"
    fi
done
info "policy artifacts: ${CK_ARTIFACTS_PRESENT}/${#CK_ARTIFACTS[@]} required by the roster are deployed"

# ---------------------------------------------------------------------------
# 8. Deploy script for subsequent updates
# ---------------------------------------------------------------------------

step "Update script"

# Install the version-controlled script rather than generating a copy. The
# generated heredoc that used to live here was byte-identical to
# docs/deploy/update.sh, which meant two copies of the rollback logic with
# nothing to detect drift -- and the box ran the copy nobody reviewed. The
# file arrives with the clone, so there is nothing to duplicate.
CK_UPDATE_SRC="${CK_BUILD_DIR}/docs/deploy/update.sh"
[[ -f "$CK_UPDATE_SRC" ]] || die "missing $CK_UPDATE_SRC — the checkout is older than this provisioning script"
install -o root -g root -m 755 "$CK_UPDATE_SRC" /root/update.sh

# Paths live here so update.sh has no hardcoded layout to disagree with. It
# sources this if present and falls back to the same defaults otherwise.
install -o root -g root -m 644 /dev/null /etc/default/cloudkitty-deploy
cat > /etc/default/cloudkitty-deploy <<EOF
# Written by provision-cloudkitty.sh. Consumed by /root/update.sh.
CK_BUILD_DIR=${CK_BUILD_DIR}
CK_APP_DIR=${CK_APP_DIR}
CK_STATE_DIR=${CK_STATE_DIR}
CK_USER=${CK_USER}
# Where the world server listens, so a deploy can probe it for real rather
# than trusting systemd's "active".
CK_UPSTREAM=${CK_PROXY_UPSTREAM}
EOF
info "installed /root/update.sh from the checkout + /etc/default/cloudkitty-deploy"

# ---------------------------------------------------------------------------
# 9. systemd unit
# ---------------------------------------------------------------------------

step "systemd: cloudkitty.service"

{
cat <<EOF
[Unit]
Description=CloudKitty world server
After=network-online.target
Wants=network-online.target

# These are [Unit] keys, not [Service] ones — they moved in systemd 229, and
# systemd silently ignores them (with a log warning) if put beside RestartSec.
StartLimitIntervalSec=300
StartLimitBurst=5

[Service]
User=${CK_USER}
Group=${CK_USER}
WorkingDirectory=${CK_APP_DIR}
ExecStart=${CK_APP_DIR}/cloudkitty-server --config ${CK_APP_DIR}/cloudkitty.toml --snapshot ${CK_STATE_DIR}/snapshot.json

# Graceful shutdown — "letting the kitties settle", final world save included —
# listens for SIGINT only. systemd's default SIGTERM would skip it.
KillSignal=SIGINT
TimeoutStopSec=30
Restart=on-failure

# RestartSec=2 against systemd's default limit (5 starts per 10s) burns every
# attempt in 8 seconds, so any fault taking longer than that to clear leaves
# the unit failed permanently and the site down until someone runs
# \`systemctl reset-failed\`. Five-second spacing (with the wider window set
# in [Unit]) rides out a slow dependency without hiding a genuine crash loop.
RestartSec=5
EOF

if [[ "$CK_HARDEN_UNIT" == "1" ]]; then
cat <<EOF

# --- sandboxing ---
# The whole filesystem is read-only to this service except ${CK_STATE_DIR},
# which holds the world and nothing else. The binary, the config, client/ and
# policies/ are root-owned and outside ReadWritePaths, so a compromised server
# cannot rewrite the code it will be restarted into.
#
# ProcSubset=pid is deliberately absent: it hides /proc/meminfo and
# /proc/cpuinfo, which allocators and thread pools read during startup, and
# the failure would not surface until the first manual start.
NoNewPrivileges=true
ProtectSystem=strict
ReadWritePaths=${CK_STATE_DIR}
ProtectHome=true
PrivateTmp=true
PrivateDevices=true
ProtectClock=true
ProtectHostname=true
ProtectKernelTunables=true
ProtectKernelModules=true
ProtectKernelLogs=true
ProtectControlGroups=true
ProtectProc=invisible
RestrictAddressFamilies=AF_UNIX AF_INET AF_INET6
RestrictNamespaces=true
RestrictRealtime=true
RestrictSUIDSGID=true
LockPersonality=true
MemoryDenyWriteExecute=true
SystemCallFilter=@system-service
SystemCallErrorNumber=EPERM
SystemCallArchitectures=native
UMask=0027
MemoryMax=${CK_MEMORY_MAX}
EOF
fi

cat <<EOF

[Install]
WantedBy=multi-user.target
EOF
} > /etc/systemd/system/cloudkitty.service

systemctl daemon-reload
systemctl enable cloudkitty >/dev/null
info "installed and enabled (not started)"
if [[ "$CK_HARDEN_UNIT" == "1" ]]; then
    info "sandboxing on; verify later with: systemd-analyze security cloudkitty"
fi

# ---------------------------------------------------------------------------
# 10. Caddy (official repo)
# ---------------------------------------------------------------------------

step "Caddy"

# Upstream Caddy, not Ubuntu universe's: the proxy is the box's main attack
# surface (owner, 2026-08-04), so it tracks upstream security releases rather
# than universe's frozen 2.6.x.
#
# Guard on the sources list, not the keyring: a box carrying the keyring but no
# list would otherwise skip the whole block and silently install Ubuntu
# universe's caddy 2.6.x, which satisfies `apt-get install caddy` just as well.
if [[ ! -f /etc/apt/sources.list.d/caddy-stable.list ]]; then
    # Pin the signing key by fingerprint, the same way github.com's host key is
    # pinned above. Fetching a key over TLS and immediately trusting it makes
    # every later apt operation -- including unattended-upgrades, forever --
    # trust whoever answered that one request. Verify before installing it.
    caddy_key="$(mktemp)"
    curl -1sLf 'https://dl.cloudsmith.io/public/caddy/stable/gpg.key' \
        | gpg --dearmor > "$caddy_key" || die "could not fetch the Caddy signing key"
    caddy_fp="$(gpg --show-keys --with-colons --fingerprint "$caddy_key" \
        | awk -F: '/^fpr:/ {print $10; exit}')"
    if [[ "$caddy_fp" != "$CADDY_GPG_FP" ]]; then
        rm -f "$caddy_key"
        die "Caddy signing key fingerprint mismatch: got ${caddy_fp:-none}, expected $CADDY_GPG_FP
    Either the key rotated (check https://caddyserver.com/docs/install#debian-ubuntu-raspbian
    and update CADDY_GPG_FP) or the download was tampered with. Refusing to
    trust it -- an apt signing key is permanent root-level trust."
    fi
    install -m 644 "$caddy_key" /usr/share/keyrings/caddy-stable-archive-keyring.gpg
    rm -f "$caddy_key"
    info "pinned Caddy signing key ($caddy_fp)"

    # Write the source line locally rather than curling it: a fetched
    # sources.list can name any host, which would route apt around the key we
    # just verified. signed-by= binds this repo to that one key.
    cat > /etc/apt/sources.list.d/caddy-stable.list <<EOF
deb [signed-by=/usr/share/keyrings/caddy-stable-archive-keyring.gpg] https://dl.cloudsmith.io/public/caddy/stable/deb/debian any-version main
EOF
    apt-get update -qq
fi
apt-get install -y -qq caddy

# Confirm what we actually got, rather than trusting that the repo add worked.
#
# Read the output into a variable first, rather than piping into `grep -q`.
# `grep -q` exits the instant it matches, apt-cache dies of SIGPIPE still
# writing, and `set -o pipefail` hands the pipeline apt-cache's 141 -- so the
# check reports failure precisely when it succeeds. It aborted a real
# provisioning run here on 2026-08-04, with a message blaming the repo.
CK_CADDY_POLICY="$(apt-cache policy caddy)"

# Check the INSTALLED version's origin, not merely that the repo is configured.
# `apt-cache policy` lists every known source, so a bare grep for the cloudsmith
# host passes even when the installed line is universe's 2.6.x from
# /var/lib/dpkg/status -- exactly the outcome this guard exists to prevent.
# The `***` marker flags the installed version; the line after it names where
# that version came from.
CK_CADDY_ORIGIN="$(grep -A1 '^ \*\*\*' <<< "$CK_CADDY_POLICY" | tail -n1 || true)"
grep -q 'dl\.cloudsmith\.io' <<< "$CK_CADDY_ORIGIN" \
    || die "the INSTALLED caddy did not come from the official repo.
    apt-cache policy caddy reports its origin as:
      ${CK_CADDY_ORIGIN:-<none>}
    Ubuntu universe ships a frozen 2.6.x that satisfies \`apt-get install caddy\`
    just as well. Remove it (apt-get purge caddy) and re-run, or check
    /etc/apt/preferences.d/ for a pin favouring universe."
info "installed $(caddy version 2>/dev/null | head -n1 || true) from the official repo"

# The package starts Caddy on the stock welcome-page config; stop it while we
# install the real one so nothing ever serves the wrong thing.
systemctl stop caddy || true

install -d -o caddy -g caddy -m 755 /var/log/caddy

# Caddy requires a space after each comma in a site address list.
CADDY_SITES=""
for d in "${CK_DOMAIN_LIST[@]}"; do
    CADDY_SITES="${CADDY_SITES:+${CADDY_SITES}, }${d}"
done

{
cat <<EOF
${CADDY_SITES} {
	encode zstd gzip
	reverse_proxy ${CK_PROXY_UPSTREAM}
	header {
		X-Content-Type-Options nosniff
		X-Frame-Options DENY
		Referrer-Policy no-referrer
	}
	log {
		output file /var/log/caddy/cloudkitty.log {
			roll_size 5MB
			roll_keep 3
			roll_keep_for 168h
		}
	}
}
EOF

for d in "${CK_DOMAIN_LIST[@]}"; do
cat <<EOF

www.${d} {
	redir https://${d}{uri} permanent
}
EOF
done
} > /etc/caddy/Caddyfile

caddy fmt --overwrite /etc/caddy/Caddyfile
caddy validate --config /etc/caddy/Caddyfile >/dev/null || die "Caddyfile failed validation"

# `caddy validate` provisions the config for real, and provisioning the log
# directive opens the file -- as root, from here. Left root-owned, the service
# (User=caddy) then fails every start and reload with "permission denied" on its
# own log, long after validation said the config was fine. Re-own after
# validating, never before. Observed on this box 2026-08-04.
chown -R caddy:caddy /var/log/caddy

systemctl enable caddy >/dev/null
info "Caddyfile written for: ${CADDY_SITES} (and www redirects)"
info "enabled (not started) — first start issues certificates"

# ---------------------------------------------------------------------------
# 11. Firewall
# ---------------------------------------------------------------------------

step "ufw"

# Open the port sshd actually listens on, not the OpenSSH profile's hardcoded
# 22 — `ufw enable` below applies a default-deny policy to the live session.
# `sshd -T` reports sshd_config's Port, which on 24.04 is NOT necessarily what
# sshd listens on: ssh.socket is enabled by default and its ListenStream= does
# the binding, so a host moved to another port the supported way still reports
# 22 here. Ask the socket first, fall back to the config, and only then to 22.
SSH_PORTS=""
if systemctl is-enabled --quiet ssh.socket 2>/dev/null; then
    SSH_PORTS="$(systemctl show ssh.socket -p ListenStream --value 2>/dev/null \
        | awk -F: 'NF{print $NF}' | sort -u || true)"
    if [[ -n "$SSH_PORTS" ]]; then
        info "ssh.socket is active; ports from ListenStream"
    fi
fi
if [[ -z "$SSH_PORTS" ]]; then
    SSH_PORTS="$(sshd -T 2>/dev/null | awk '/^port /{print $2}' || true)"
fi
# Never silently assume 22: `ufw enable` applies default-deny, and guessing
# wrong locks out the next login (the current session survives on the
# ESTABLISHED rule, so the run looks like it succeeded).
[[ -n "$SSH_PORTS" ]] || die "could not determine the port sshd listens on \
(neither ssh.socket ListenStream nor sshd -T answered).
    Refusing to enable a default-deny firewall on a guess. Set the port
    explicitly and re-run, or provision with the firewall step reviewed by hand."

ufw --force reset >/dev/null 2>&1 || true
ufw default deny incoming >/dev/null
ufw default allow outgoing >/dev/null
for p in $SSH_PORTS; do
    ufw allow "${p}/tcp" >/dev/null
done
ufw allow 80/tcp >/dev/null    # ACME HTTP-01 + the http->https redirect
ufw allow 443/tcp >/dev/null   # the public face
ufw --force enable >/dev/null
info "active: ${SSH_PORTS//$'\n'/, } (ssh), 80, 443 in; ${CK_BIND_PORT} stays loopback-only"

# ---------------------------------------------------------------------------
# 12. Hardening
# ---------------------------------------------------------------------------

if [[ "$CK_HARDEN_SSH" == "1" ]]; then
    step "SSH hardening"

    # The drop-in disables password auth for every account, so the guard has to
    # check every account that can log in — not just root.
    KEYLESS=()
    while IFS=: read -r acct _ uid _ _ home shell; do
        case "$shell" in
            */nologin|*/false|'') continue ;;
        esac
        [[ "$uid" -eq 0 || "$uid" -ge 1000 ]] || continue
        [[ -s "${home}/.ssh/authorized_keys" ]] || KEYLESS+=("$acct")
    done < /etc/passwd

    # This box is key-only by policy (owner, 2026-08-04). A keyless
    # login-capable account is therefore a provisioning error to be fixed, not
    # a reason to leave password auth on: the old behaviour skipped hardening
    # entirely -- including for root -- behind a single warning, and still
    # exited 0. Fail loudly instead, and say exactly how to proceed.
    if [[ ${#KEYLESS[@]} -gt 0 ]]; then
        die "no authorized_keys for: ${KEYLESS[*]}
    This host is key-only by policy, so provisioning stops rather than
    leaving password authentication enabled. Either install a key for each
    account listed, remove/disable the accounts, or re-run with
    CK_HARDEN_SSH=0 to keep password auth on deliberately."
    fi

    # 00-, not 99-: sshd takes the FIRST value it obtains for each keyword,
    # /etc/ssh/sshd_config Includes sshd_config.d/*.conf at the top, and the
    # glob expands in lexical order. Ubuntu cloud images ship
    # 50-cloud-init.conf carrying `PasswordAuthentication yes`, which at 99-
    # silently outranked this file: the run printed "password auth disabled"
    # while the box still accepted passwords. Numbering it 00- makes this the
    # first value read, and the verification below proves it took effect.
    CK_SSHD_DROPIN=/etc/ssh/sshd_config.d/00-cloudkitty-hardening.conf
    rm -f /etc/ssh/sshd_config.d/99-cloudkitty-hardening.conf
    cat > "$CK_SSHD_DROPIN" <<'EOF'
# Keys only. Written by provision-cloudkitty.sh.
# Must sort BEFORE any other drop-in: sshd uses the first value per keyword.
PasswordAuthentication no
KbdInteractiveAuthentication no
PermitEmptyPasswords no
PermitRootLogin prohibit-password
EOF

    if ! sshd -t; then
        rm -f "$CK_SSHD_DROPIN"
        die "sshd rejected the hardening drop-in; reverted, nothing changed"
    fi

    # Assert the EFFECTIVE config, not the file we just wrote. `sshd -T`
    # resolves every Include in order, so this is the only check that can tell
    # "hardened" apart from "outranked by a drop-in we did not write".
    CK_SSHD_EFFECTIVE="$(sshd -T 2>/dev/null || true)"
    [[ -n "$CK_SSHD_EFFECTIVE" ]] || die "could not read the effective sshd config (sshd -T)"
    for kv in passwordauthentication=no kbdinteractiveauthentication=no permitemptypasswords=no; do
        if ! grep -qixF "${kv/=/ }" <<< "$CK_SSHD_EFFECTIVE"; then
            rm -f "$CK_SSHD_DROPIN"
            die "hardening did not take effect: sshd still reports \
'$(grep -i "^${kv%%=*} " <<< "$CK_SSHD_EFFECTIVE" || echo "${kv%%=*} (unset)")'.
    Another drop-in in /etc/ssh/sshd_config.d/ outranks ours, or the main
    sshd_config sets it before the Include. Reverted; nothing changed.
    Inspect with: grep -r . /etc/ssh/sshd_config.d/ /etc/ssh/sshd_config"
        fi
    done

    # 24.04 socket-activates sshd, so per-connection instances pick the new
    # config up anyway; reload the service if one is running.
    systemctl reload ssh 2>/dev/null || systemctl restart ssh 2>/dev/null || true
    info "password auth disabled and verified via sshd -T; root login key-only"
fi

if [[ "$CK_UNATTENDED" == "1" ]]; then
    step "Unattended security upgrades"
    apt-get install -y -qq unattended-upgrades
    cat > /etc/apt/apt.conf.d/20auto-upgrades <<'EOF'
APT::Periodic::Update-Package-Lists "1";
APT::Periodic::Unattended-Upgrade "1";
EOF
    # Defaults already restrict to the security pocket; the one thing worth
    # overriding is the reboot, which would restart the world unattended.
    cat > /etc/apt/apt.conf.d/52unattended-upgrades-local <<'EOF'
Unattended-Upgrade::Automatic-Reboot "false";
EOF
    systemctl enable --now unattended-upgrades >/dev/null
    info "security pocket only, no automatic reboot (watch /var/run/reboot-required)"
fi

if [[ "$CK_JOURNAL_CAP" == "1" ]]; then
    step "journald cap"
    install -d /etc/systemd/journald.conf.d
    cat > /etc/systemd/journald.conf.d/99-cloudkitty.conf <<'EOF'
[Journal]
SystemMaxUse=200M
EOF
    systemctl restart systemd-journald
    info "capped at 200M (Caddy's access log self-rotates via roll_size)"
fi

if [[ "$CK_FAIL2BAN" == "1" ]]; then
    step "fail2ban"
    # python3-systemd is what the systemd backend needs; the package only
    # recommends it, and without it the jail fails to start.
    apt-get install -y -qq fail2ban python3-systemd
    cat > /etc/fail2ban/jail.d/sshd.local <<'EOF'
[sshd]
enabled = true
backend = systemd
maxretry = 5
findtime = 10m
bantime = 1h
EOF
    # An optional hardening extra must not fail a run that is otherwise done.
    if systemctl enable --now fail2ban >/dev/null 2>&1; then
        info "sshd jail: 5 failures in 10m -> 1h ban"
    else
        warn "fail2ban failed to start; everything else is provisioned. Check: journalctl -u fail2ban"
    fi
fi

# ---------------------------------------------------------------------------
# Done
# ---------------------------------------------------------------------------

step "Provisioned"

MISSING_ARTIFACTS=()
for rel in "${CK_ARTIFACTS[@]}"; do
    case "$rel" in
        /*) target="$rel" ;;
        *)  target="${CK_APP_DIR}/${rel}" ;;
    esac
    if [[ ! -f "$target" ]]; then
        MISSING_ARTIFACTS+=("$target")
    fi
done

cat <<EOF

    Installed and enabled, nothing started yet.

      app        ${CK_APP_DIR}          (${CK_USER}, nologin)
      source     ${CK_BUILD_DIR}        (root builds; deploy key pulls)
      update     /root/update.sh   (--client-only: viewer alone; --fresh: retire the world)
      service    /etc/systemd/system/cloudkitty.service
      proxy      /etc/caddy/Caddyfile -> ${CK_BIND}
      firewall   ${SSH_PORTS//$'\n'/, } (ssh), 80, 443

    Before starting:

      1. Point DNS for ${CADDY_SITES} (and the www.* names) at ${PUBLIC_ADDR}.
         Caddy issues certificates on its first start and will fail loudly
         against stale DNS.
EOF

if [[ ${#MISSING_ARTIFACTS[@]} -gt 0 ]]; then
cat <<EOF

      2. Supply the RL policy artifact(s) below. A kitty in the roster names
         each one, so the server refuses to start without them. Deployed
         artifacts belong in the committed policies/ directory, where they
         deploy with everything else — one missing here is either a config
         naming a path outside the tree, or an artifact that never got
         committed (policies/README.md). From your local checkout:

$(for a in "${MISSING_ARTIFACTS[@]}"; do echo "           scp <local-path> root@${PUBLIC_ADDR}:${a}"; done)

      3. Place the world at ${CK_STATE_DIR}/snapshot.json if resuming an
         existing one, owned by ${CK_USER}:

           scp snapshot.json root@${PUBLIC_ADDR}:${CK_STATE_DIR}/
           ssh root@${PUBLIC_ADDR} chown -R ${CK_USER}:${CK_USER} ${CK_STATE_DIR}
EOF
else
cat <<EOF

      2. Place the world at ${CK_STATE_DIR}/snapshot.json if resuming an
         existing one, owned by ${CK_USER}:

           scp snapshot.json root@${PUBLIC_ADDR}:${CK_STATE_DIR}/
           ssh root@${PUBLIC_ADDR} chown -R ${CK_USER}:${CK_USER} ${CK_STATE_DIR}
EOF
fi

cat <<EOF

    Then:

      systemctl start cloudkitty && journalctl -u cloudkitty -f
      systemctl start caddy      && journalctl -u caddy -f
      curl -sS localhost:${CK_BIND_PORT}/world | head -c 200

EOF

if [[ "$CK_START_SERVICES" == "1" ]]; then
    step "Starting services (CK_START_SERVICES=1)"
    # Unguarded, a failed start would abort before Caddy starts and before the
    # status output that explains why.
    CK_START_FAILED=0
    systemctl start cloudkitty || { warn "cloudkitty failed to start"; CK_START_FAILED=1; }
    systemctl start caddy      || { warn "caddy failed to start";      CK_START_FAILED=1; }
    sleep 3
    for svc in cloudkitty caddy; do
        if ! systemctl is-active --quiet "$svc"; then
            warn "$svc is not active"
            CK_START_FAILED=1
        fi
    done
    systemctl --no-pager --lines=10 status cloudkitty || true
    systemctl --no-pager --lines=10 status caddy || true
    # Exit non-zero when asked to start and the services are not up: a caller
    # must be able to tell "provisioned and serving" from "provisioned and
    # dead", and a warning printed after the "Provisioned" banner cannot.
    if [[ "$CK_START_FAILED" == "1" ]]; then
        die "provisioning finished but the services are not running (see status above)"
    fi
    info "cloudkitty and caddy are running"
fi
