#!/usr/bin/env bash
#
# Pull, rebuild, and deploy the world server.
#
# Deploys the config and the policy artifacts too, not just the binary and the
# viewer: a commit that reseats a kitty or relocates a .ckpolicy is otherwise a
# silent no-op on the served world.
#
# `update.sh --client-only` deploys ONLY the viewer: pull, rsync client/,
# done. No build, no restart, no binary/config/policy swap — the server reads
# client files from disk per request (ServeDir), so new assets are live
# immediately. This is the only safe deploy while main carries a newer
# observation schema than the served policy artifacts speak (the exp-003
# window): a full deploy would build that newer binary, which then refuses to
# boot against the deployed .ckpolicy files. Client fixes must not be able to
# take the world down.
#
# The resume guard fingerprints world size, seed, and the roster's kitty ids
# (Config::fingerprint). A config that changes any of those makes the server
# refuse to resume the saved world rather than discard it — so it fails to
# start, and this script puts the old config back and brings the old world up
# again instead of leaving the site down.
#
# Installed to /root/update.sh by provision-cloudkitty.sh, which also writes
# /etc/default/cloudkitty-deploy with this box's paths. This file is the only
# copy: it used to be duplicated as a heredoc inside the provisioning script,
# which meant the reviewed copy and the running copy could drift apart.

set -euo pipefail

CLIENT_ONLY=0
case "${1:-}" in
    "") ;;
    --client-only) CLIENT_ONLY=1 ;;
    *)
        echo "usage: update.sh [--client-only]" >&2
        echo "  (no args)      full deploy: pull, build, swap binary+config+policies+client" >&2
        echo "  --client-only  pull and deploy client/ only; server untouched" >&2
        exit 2
        ;;
esac

# Paths come from provisioning; the defaults match its defaults so the script
# still runs on a box provisioned before the env file existed.
if [[ -r /etc/default/cloudkitty-deploy ]]; then
    # shellcheck source=/dev/null
    . /etc/default/cloudkitty-deploy
fi

REPO="${CK_BUILD_DIR:-/root/cloudkitty}"
APP="${CK_APP_DIR:-/opt/cloudkitty}"
STATE="${CK_STATE_DIR:-${APP}/state}"
SVC_USER="${CK_USER:-cloudkitty}"
UPSTREAM="${CK_UPSTREAM:-127.0.0.1:8090}"
BACKUP_ROOT=/root/cloudkitty-deploy-backup
KEEP_BACKUPS="${CK_KEEP_BACKUPS:-5}"

# Declared up front so the ERR trap can reference them no matter how early it
# fires -- under `set -u` an unbound expansion inside the trap would replace a
# useful diagnostic with a confusing one. Filled in later.
WORLD=""
LEGACY_LAYOUT=0
BACKUP="(not created yet)"

# One deploy at a time. Two concurrent runs interleave a stop, an rsync
# --delete and a world copy, leaving a backup holding one run's config beside
# another run's world with no way to tell afterwards.
exec 9>/run/cloudkitty-deploy.lock
flock -n 9 || { echo "another deploy is already running (/run/cloudkitty-deploy.lock)" >&2; exit 1; }

log() { printf '==> %s\n' "$*"; }

# Everything from `systemctl stop` onward runs with the site down. Without a
# trap, an rsync or chown failure in that window exits on `set -e` with the
# service stopped, no rollback attempted, and no word about where the backup
# is — the operator is left with a dark site and no map.
DEPLOY_STARTED=0
# shellcheck disable=SC2329  # invoked indirectly by `trap on_error ERR` below
on_error() {
    local rc=$?
    [[ "$DEPLOY_STARTED" == "1" ]] || exit "$rc"
    echo >&2
    echo "!! deploy aborted mid-flight (exit $rc) — the site may be down" >&2
    echo "   backup of the previous state: ${BACKUP}" >&2
    echo "   to restore by hand:" >&2
    echo "     systemctl stop cloudkitty" >&2
    echo "     cp -a ${BACKUP}/cloudkitty-server ${APP}/cloudkitty-server" >&2
    echo "     cp -a ${BACKUP}/cloudkitty.toml   ${APP}/cloudkitty.toml" >&2
    echo "     rsync -a --delete ${BACKUP}/policies/ ${APP}/policies/" >&2
    echo "     cp -a ${BACKUP}/snapshot.json ${WORLD:-${STATE}/snapshot.json}   # only if that backup exists" >&2
    echo "     systemctl reset-failed cloudkitty && systemctl start cloudkitty" >&2
    exit "$rc"
}
trap on_error ERR

# Probe the world server itself rather than trusting systemd. The unit is
# Type=simple, so it is "active" the instant exec succeeds: a server that
# binds and then dies loading a policy is reported healthy by `is-active` and
# a fixed sleep, which is how a dead deploy gets an exit 0.
wait_healthy() {
    local deadline=$((SECONDS + 45))
    while (( SECONDS < deadline )); do
        if ! systemctl is-active --quiet cloudkitty; then
            sleep 1
            continue
        fi
        if curl -fsS --max-time 3 "http://${UPSTREAM}/world" >/dev/null 2>&1; then
            # Serving. Confirm it is still up a beat later, so a server that
            # answers once and then falls over is not counted as healthy.
            sleep 3
            if systemctl is-active --quiet cloudkitty \
               && curl -fsS --max-time 3 "http://${UPSTREAM}/world" >/dev/null 2>&1; then
                return 0
            fi
        fi
        sleep 2
    done
    return 1
}

cd "$REPO"
git pull --ff-only
DEPLOYED_REV="$(git rev-parse --short HEAD)"

if [[ "$CLIENT_ONLY" == "1" ]]; then
    log "client-only: deploying viewer assets from ${DEPLOYED_REV}; server untouched"
    # No backup slot: the client is never rolled back by the full deploy
    # either ("it is static and does not affect startup"), and every prior
    # version is one `git checkout` away in this checkout. If the rsync dies
    # midway the site stays up (the server keeps running); rerun to finish.
    rsync -a --delete client/ "${APP}/client/"
    chown -R root:root "${APP}/client"
    if curl -fsS --max-time 3 "http://${UPSTREAM}/world" >/dev/null 2>&1; then
        log "client ${DEPLOYED_REV} live — server still serving"
    else
        log "client ${DEPLOYED_REV} deployed — but the server is not answering" \
            "(it was not touched by this run; check systemctl status cloudkitty)"
    fi
    exit 0
fi

log "building ${DEPLOYED_REV}"

# Before touching anything: a release build plus a full copy of the world can
# fill a small droplet, and a truncated backup is worse than none.
AVAIL_KB="$(df -Pk /root | awk 'NR==2{print $4}')"
if (( AVAIL_KB < 2097152 )); then
    echo "only $((AVAIL_KB / 1024)) MB free on /root; want at least 2048 MB for a build + backup" >&2
    exit 1
fi

cargo build --release -p cloudkitty-server

# Timestamped generations, not one overwritten slot. With a single slot, the
# second deploy after a bad one replaces the last good world with the bad one,
# and there is no other copy on the box.
BACKUP="${BACKUP_ROOT}/$(date +%Y%m%d-%H%M%S)"
install -d -m 700 "$BACKUP"

# The binary is backed up too: a start failure after a successful build is
# usually the binary, not the config, and restoring config alone just restarts
# the same broken build.
cp -a "${APP}/cloudkitty-server" "${BACKUP}/cloudkitty-server"
cp -a "${APP}/cloudkitty.toml"   "${BACKUP}/cloudkitty.toml"
if [[ -d "${APP}/policies" ]]; then
    rsync -a "${APP}/policies/" "${BACKUP}/policies/"
fi

DEPLOY_STARTED=1
systemctl stop cloudkitty          # SIGINT: the world takes its final save

# Find the world before backing it up. Boxes provisioned before the state/
# split keep it in the app root, and their systemd unit passes no --snapshot,
# so it is still the live world there. Looking only in state/ on such a box
# would report "nothing to back up" and sail on -- the same silent-safety-net
# failure this backup exists to prevent.
if [[ -f "${STATE}/snapshot.json" ]]; then
    WORLD="${STATE}/snapshot.json"
elif [[ -f "${APP}/snapshot.json" ]]; then
    WORLD="${APP}/snapshot.json"
    LEGACY_LAYOUT=1
fi

# Copy the world only if there is one, and let a real failure be a real
# failure. The old blanket `2>/dev/null || true` hid ENOSPC and permission
# errors as readily as the legitimate "no world yet" case, and both closing
# messages then pointed the operator at a file that was never written.
if [[ -n "$WORLD" ]]; then
    cp -a "$WORLD" "${BACKUP}/snapshot.json"
    log "world backed up from ${WORLD} to ${BACKUP}/snapshot.json"
else
    log "no world found in ${STATE} or ${APP} yet — nothing to back up"
fi

if [[ "$LEGACY_LAYOUT" == "1" ]]; then
    cat >&2 <<MSG

    NOTE: the world is still at ${APP}/snapshot.json, the pre-state/ layout.
    This deploy leaves it there and backs it up from there, so nothing is
    lost. To move to the sandboxed layout (the service can no longer rewrite
    its own binary), after this deploy settles:

      systemctl stop cloudkitty
      install -d -o ${SVC_USER} -g ${SVC_USER} -m 750 ${STATE}
      mv ${APP}/snapshot.json ${STATE}/snapshot.json
      chown ${SVC_USER}:${SVC_USER} ${STATE}/snapshot.json
      # then add to ExecStart in /etc/systemd/system/cloudkitty.service:
      #   --snapshot ${STATE}/snapshot.json
      # and set: ReadWritePaths=${STATE}
      systemctl daemon-reload && systemctl start cloudkitty

MSG
fi

install -o root -g root -m 755 target/release/cloudkitty-server "${APP}/cloudkitty-server"
# --delete, not cp -r: a merge would leave assets deleted upstream behind, and
# the server would keep serving them.
rsync -a --delete client/ "${APP}/client/"
install -o root -g root -m 644 cloudkitty.toml "${APP}/cloudkitty.toml"
if [[ -d policies ]]; then
    rsync -a --delete policies/ "${APP}/policies/"
fi
# Only the state directory belongs to the service; everything it reads stays
# root-owned so a compromised server cannot rewrite its own binary.
chown -R root:root "${APP}/client"
if [[ -d "${APP}/policies" ]]; then
    chown -R root:root "${APP}/policies"
fi
install -d -o "$SVC_USER" -g "$SVC_USER" -m 750 "$STATE"
chown -R "${SVC_USER}:${SVC_USER}" "$STATE"

# A previous crash loop may have burned the unit's start limit; without this
# `systemctl start` fails with "start request repeated too quickly" and a
# perfectly good deploy looks broken.
systemctl reset-failed cloudkitty 2>/dev/null || true
systemctl start cloudkitty || true

if wait_healthy; then
    trap - ERR
    systemctl --no-pager --lines=5 status cloudkitty
    log "deployed ${DEPLOYED_REV} — serving at http://${UPSTREAM}/world"
    # Prune old generations, newest kept. Guarded: an empty or missing backup
    # root must not fail a deploy that already succeeded.
    if [[ -d "$BACKUP_ROOT" ]]; then
        # shellcheck disable=SC2012
        stale="$(ls -1dt "${BACKUP_ROOT}"/*/ 2>/dev/null | tail -n "+$((KEEP_BACKUPS + 1))" || true)"
        if [[ -n "$stale" ]]; then
            while read -r old; do
                if [[ -n "$old" ]]; then
                    rm -rf "$old"
                fi
            done <<< "$stale"
        fi
    fi
    exit 0
fi

echo >&2
echo "!! cloudkitty did not come up — restoring the previous binary, config and policies" >&2
journalctl -u cloudkitty --no-pager --lines=15 -o cat >&2

# The rollback must not itself abort on `set -e`: if the condition that broke
# the deploy also breaks the restore (a full disk, most obviously), dying here
# would leave the operator without the closing message that says where the
# world and the previous build are.
trap - ERR
set +e

systemctl stop cloudkitty
cp -a "${BACKUP}/cloudkitty-server" "${APP}/cloudkitty-server"
cp -a "${BACKUP}/cloudkitty.toml"   "${APP}/cloudkitty.toml"
if [[ -d "${BACKUP}/policies" ]]; then
    rsync -a --delete "${BACKUP}/policies/" "${APP}/policies/"
fi
chown -R root:root "${APP}/client"
if [[ -d "${APP}/policies" ]]; then
    chown -R root:root "${APP}/policies"
fi
chown -R "${SVC_USER}:${SVC_USER}" "$STATE"
systemctl reset-failed cloudkitty 2>/dev/null
systemctl start cloudkitty

if wait_healthy; then
    cat >&2 <<MSG

    Rolled back: the previous binary, config and policy artifacts are deployed
    and the world is serving again. The new viewer (client/) is still in place —
    it is static and does not affect startup.

    If the new config changes world size, seed, or the roster's kitty ids,
    the saved world cannot resume it. Options:
      - keep the old shape, or
      - start a new world:  cd ${APP} && ./cloudkitty-server --config cloudkitty.toml \\
                                --snapshot ${STATE}/snapshot.json --fresh
        (--fresh moves the old save to snapshot.json.<timestamp>.bak first)

    This deploy's backup, including the world as of the stop, is in ${BACKUP}.
MSG
else
    cat >&2 <<MSG

    Rollback did not bring it up either. Everything from before this deploy is
    in ${BACKUP}:
      cloudkitty-server   the binary that was serving
      cloudkitty.toml     the config it was serving
      policies/           the artifacts that config names
      snapshot.json       the world as of the stop (absent if none existed)

    Check: journalctl -u cloudkitty -n 50
    If the unit is stuck: systemctl reset-failed cloudkitty
MSG
fi

exit 1
