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
CK_REPO="${CK_REPO:-elizabeth-kelly-public/cloudkitty}"
CK_BRANCH="${CK_BRANCH:-main}"
CK_BUILD_DIR="${CK_BUILD_DIR:-/root/cloudkitty}"     # where root builds
CK_APP_DIR="${CK_APP_DIR:-/opt/cloudkitty}"          # what the service runs
CK_USER="${CK_USER:-cloudkitty}"
CK_DEPLOY_KEY="${CK_DEPLOY_KEY:-/root/.ssh/cloudkitty-server}"

# --- public face -----------------------------------------------------------
# Both domains are served by one site block; the www variants redirect to them.
# There is deliberately no port knob: the port comes from `bind` in the
# installed cloudkitty.toml (see "Proxy target" in step 7).
CK_DOMAINS="${CK_DOMAINS:-cloudkitty.ai kitties.ai}"

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

if [[ -r /etc/os-release ]]; then
    . /etc/os-release
    [[ "${ID:-}" == "ubuntu" ]] || warn "built for Ubuntu; found ID=${ID:-unknown}"
    [[ "${VERSION_ID:-}" == "24.04" ]] || warn "built for Ubuntu 24.04; found ${VERSION_ID:-unknown}"
fi

# Fresh-box guard: refuse to run over an existing install.
for path in "$CK_APP_DIR" "$CK_BUILD_DIR" /etc/systemd/system/cloudkitty.service; do
    if [[ -e "$path" ]]; then
        die "$path already exists — this script is fresh-box only"
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
    got="$(printf '%s\n' "$scanned" | ssh-keygen -lf - | awk '{print $2}')"
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

install -o "$CK_USER" -g "$CK_USER" -m 755 "$BIN" "${CK_APP_DIR}/cloudkitty-server"
install -o "$CK_USER" -g "$CK_USER" -m 644 "${CK_BUILD_DIR}/cloudkitty.toml" "${CK_APP_DIR}/cloudkitty.toml"
rsync -a --delete "${CK_BUILD_DIR}/client/" "${CK_APP_DIR}/client/"
# The deployed policy artifacts are committed to policies/ (owner decision
# 2026-07-31, policies/README.md), so they arrive with the clone and deploy
# exactly like the viewer -- same --delete, for the same reason: a retired
# .ckpolicy left behind is one the config could still name.
if [[ -d "${CK_BUILD_DIR}/policies" ]]; then
    rsync -a --delete "${CK_BUILD_DIR}/policies/" "${CK_APP_DIR}/policies/"
fi
chown -R "$CK_USER:$CK_USER" "$CK_APP_DIR"

# --- Proxy target ----------------------------------------------------------
# One world per server, so the config is the single source of truth for the
# port: read it here and hand it to Caddy, rather than carrying a knob that can
# silently disagree with the file. The config itself is never modified.
CK_BIND="$(grep -oP '^\s*bind\s*=\s*"\K[^"]+' "${CK_APP_DIR}/cloudkitty.toml" | head -n1 || true)"
[[ -n "$CK_BIND" ]] || die "no bind = \"...\" found in ${CK_APP_DIR}/cloudkitty.toml"

case "$CK_BIND" in
    127.0.0.1:*|localhost:*|'[::1]:'*) ;;
    *) die "cloudkitty.toml binds ${CK_BIND}, not loopback — the server would be publicly reachable, bypassing Caddy" ;;
esac

CK_BIND_PORT="${CK_BIND##*:}"
info "proxy target ${CK_BIND} (from cloudkitty.toml)"

# The RL policy artifacts the config expects; read once, checked again in the
# closing summary. Anything under policies/ landed in the rsync above. A config
# may still name an artifact from outside the tree (experiments/**/artifacts/
# is gitignored), and only that kind still needs an scp target made for it.
mapfile -t CK_ARTIFACTS < <(grep -oP '^\s*artifact\s*=\s*"\K[^"]+' "${CK_APP_DIR}/cloudkitty.toml" || true)

CK_ARTIFACTS_PRESENT=0
for rel in "${CK_ARTIFACTS[@]}"; do
    if [[ -f "${CK_APP_DIR}/${rel}" ]]; then
        CK_ARTIFACTS_PRESENT=$((CK_ARTIFACTS_PRESENT + 1))
    elif [[ "$CK_MAKE_ARTIFACT_DIR" == "1" ]]; then
        install -d -o "$CK_USER" -g "$CK_USER" -m 755 "${CK_APP_DIR}/$(dirname "$rel")"
    fi
done
info "policy artifacts: ${CK_ARTIFACTS_PRESENT}/${#CK_ARTIFACTS[@]} named by the config are deployed"

# ---------------------------------------------------------------------------
# 8. Deploy script for subsequent updates
# ---------------------------------------------------------------------------

step "Update script"

cat > /root/update.sh <<EOF
#!/usr/bin/env bash
#
# Pull, rebuild, and deploy the world server.
#
# Deploys the config and the policy artifacts too, not just the binary and the
# viewer: a commit that reseats a kitty or relocates a .ckpolicy is otherwise a
# silent no-op on the served world.
#
# The resume guard fingerprints world size, seed, and the roster's kitty ids
# (Config::fingerprint). A config that changes any of those makes the server
# refuse to resume the saved world rather than discard it — so it fails to
# start, and this script puts the old config back and brings the old world up
# again instead of leaving the site down.

set -euo pipefail

export CARGO_HOME=/root/.cargo RUSTUP_HOME=/root/.rustup
export PATH="/root/.cargo/bin:\$PATH"

REPO=${CK_BUILD_DIR}
APP=${CK_APP_DIR}
SVC_USER=${CK_USER}
BACKUP=/root/cloudkitty-deploy-backup

cd "\$REPO"
git pull --ff-only
cargo build --release -p cloudkitty-server

# Keep the last-known-good config and world next to each other, before the
# service is touched. The artifacts are backed up with the config because they
# roll back with it: this deploy may rename, retire, or delete a .ckpolicy the
# old config still names, and \`rsync --delete\` below would take it away.
install -d -m 700 "\$BACKUP"
cp -a "\${APP}/cloudkitty.toml" "\${BACKUP}/cloudkitty.toml"
rm -rf "\${BACKUP}/policies"
if [[ -d "\${APP}/policies" ]]; then
    rsync -a "\${APP}/policies/" "\${BACKUP}/policies/"
fi

systemctl stop cloudkitty          # SIGINT: the world takes its final save
cp -a "\${APP}/snapshot.json" "\${BACKUP}/snapshot.json" 2>/dev/null || true

cp target/release/cloudkitty-server "\${APP}/"
# --delete, not cp -r: a merge would leave assets deleted upstream behind, and
# the server would keep serving them.
rsync -a --delete client/ "\${APP}/client/"
install -m 644 cloudkitty.toml "\${APP}/cloudkitty.toml"
if [[ -d policies ]]; then
    rsync -a --delete policies/ "\${APP}/policies/"
fi
chown -R "\${SVC_USER}:\${SVC_USER}" "\$APP"

# \`systemctl start\` returns as soon as exec succeeds, so give the world a
# moment to either come up or fall over before believing it.
systemctl start cloudkitty || true
sleep 3

if systemctl is-active --quiet cloudkitty; then
    systemctl --no-pager --lines=5 status cloudkitty
    exit 0
fi

echo >&2
echo "!! cloudkitty did not come up — restoring the previous config" >&2
journalctl -u cloudkitty --no-pager --lines=15 -o cat >&2

systemctl stop cloudkitty || true
cp -a "\${BACKUP}/cloudkitty.toml" "\${APP}/cloudkitty.toml"
if [[ -d "\${BACKUP}/policies" ]]; then
    rsync -a --delete "\${BACKUP}/policies/" "\${APP}/policies/"
fi
chown -R "\${SVC_USER}:\${SVC_USER}" "\$APP"
systemctl start cloudkitty || true
sleep 3

if systemctl is-active --quiet cloudkitty; then
    cat >&2 <<MSG

    Rolled back: the previous config and the policy artifacts it names are
    deployed and the world is serving again. The new binary and viewer are
    still in place — \${APP}/cloudkitty.toml and \${APP}/policies were reverted.

    If the new config changes world size, seed, or the roster's kitty ids,
    the saved world cannot resume it. Options:
      - keep the old shape, or
      - start a new world:  cd \${APP} && ./cloudkitty-server --config cloudkitty.toml --fresh
        (--fresh moves the old save to snapshot.json.<timestamp>.bak first)

    The world as of this deploy is saved at \${BACKUP}/snapshot.json.
MSG
else
    cat >&2 <<MSG

    Rollback did not bring it up either. The world as of this deploy is at
    \${BACKUP}/snapshot.json, the previous config at \${BACKUP}/cloudkitty.toml,
    and the artifacts it names at \${BACKUP}/policies.
    Check: journalctl -u cloudkitty -n 50
MSG
fi

exit 1
EOF
chmod +x /root/update.sh
info "wrote /root/update.sh (binary, viewer, config, policies)"

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

[Service]
User=${CK_USER}
Group=${CK_USER}
WorkingDirectory=${CK_APP_DIR}
ExecStart=${CK_APP_DIR}/cloudkitty-server --config ${CK_APP_DIR}/cloudkitty.toml

# Graceful shutdown — "letting the kitties settle", final world save included —
# listens for SIGINT only. systemd's default SIGTERM would skip it.
KillSignal=SIGINT
TimeoutStopSec=30
Restart=on-failure
RestartSec=2
EOF

if [[ "$CK_HARDEN_UNIT" == "1" ]]; then
cat <<EOF

# --- sandboxing ---
# The whole filesystem is read-only to this service except its own directory,
# which has to stay writable for snapshot.json.
#
# ProcSubset=pid is deliberately absent: it hides /proc/meminfo and
# /proc/cpuinfo, which allocators and thread pools read during startup, and
# the failure would not surface until the first manual start.
NoNewPrivileges=true
ProtectSystem=strict
ReadWritePaths=${CK_APP_DIR}
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

# Guard on the sources list, not the keyring: a box carrying the keyring but no
# list would otherwise skip the whole block and silently install Ubuntu
# universe's caddy 2.6.x, which satisfies `apt-get install caddy` just as well.
if [[ ! -f /etc/apt/sources.list.d/caddy-stable.list ]]; then
    curl -1sLf 'https://dl.cloudsmith.io/public/caddy/stable/gpg.key' \
        | gpg --dearmor --yes -o /usr/share/keyrings/caddy-stable-archive-keyring.gpg
    curl -1sLf 'https://dl.cloudsmith.io/public/caddy/stable/debian.deb.txt' \
        > /etc/apt/sources.list.d/caddy-stable.list
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
grep -q 'dl\.cloudsmith\.io' <<< "$CK_CADDY_POLICY" \
    || die "caddy did not come from the official repo — check /etc/apt/sources.list.d/caddy-stable.list"
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
	reverse_proxy 127.0.0.1:${CK_BIND_PORT}
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
SSH_PORTS="$(sshd -T 2>/dev/null | awk '/^port /{print $2}' || true)"
[[ -n "$SSH_PORTS" ]] || SSH_PORTS=22

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

    if [[ ${#KEYLESS[@]} -eq 0 ]]; then
        cat > /etc/ssh/sshd_config.d/99-cloudkitty-hardening.conf <<'EOF'
# Keys only. Written by provision-cloudkitty.sh.
PasswordAuthentication no
KbdInteractiveAuthentication no
PermitEmptyPasswords no
PermitRootLogin prohibit-password
EOF
        if sshd -t; then
            # 24.04 socket-activates sshd, so per-connection instances pick the
            # new config up anyway; reload the service if one is running.
            systemctl reload ssh 2>/dev/null || systemctl restart ssh 2>/dev/null || true
            info "password auth disabled, root login key-only"
        else
            rm -f /etc/ssh/sshd_config.d/99-cloudkitty-hardening.conf
            warn "sshd rejected the hardening drop-in; reverted, nothing changed"
        fi
    else
        warn "no authorized_keys for: ${KEYLESS[*]} — skipping, disabling password auth would lock them out"
    fi
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
    if [[ ! -f "${CK_APP_DIR}/${rel}" ]]; then
        MISSING_ARTIFACTS+=("$rel")
    fi
done

cat <<EOF

    Installed and enabled, nothing started yet.

      app        ${CK_APP_DIR}          (${CK_USER}, nologin)
      source     ${CK_BUILD_DIR}        (root builds; deploy key pulls)
      update     /root/update.sh
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

      2. Supply the RL policy artifact(s) below. The config names them and the
         server refuses to start without them. Deployed artifacts belong in the
         committed policies/ directory, where they deploy with everything else —
         one missing here is either a config naming a path outside the tree, or
         an artifact that never got committed (policies/README.md). Meanwhile,
         from your local checkout:

$(for a in "${MISSING_ARTIFACTS[@]}"; do echo "           scp $a root@${PUBLIC_ADDR}:${CK_APP_DIR}/$a"; done)
           ssh root@${PUBLIC_ADDR} chown -R ${CK_USER}:${CK_USER} ${CK_APP_DIR}

      3. Place a snapshot.json in ${CK_APP_DIR} if resuming an existing world.
EOF
else
cat <<EOF

      2. Place a snapshot.json in ${CK_APP_DIR} if resuming an existing world.
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
    systemctl start cloudkitty || warn "cloudkitty failed to start"
    systemctl start caddy || warn "caddy failed to start"
    sleep 3
    systemctl --no-pager --lines=10 status cloudkitty || true
    systemctl --no-pager --lines=10 status caddy || true
fi
