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
export PATH="/root/.cargo/bin:$PATH"

REPO=/root/cloudkitty
APP=/opt/cloudkitty
SVC_USER=cloudkitty
BACKUP=/root/cloudkitty-deploy-backup

cd "$REPO"
git pull --ff-only
cargo build --release -p cloudkitty-server

# Keep the last-known-good config and world next to each other, before the
# service is touched. The artifacts are backed up with the config because they
# roll back with it: this deploy may rename, retire, or delete a .ckpolicy the
# old config still names, and `rsync --delete` below would take it away.
install -d -m 700 "$BACKUP"
cp -a "${APP}/cloudkitty.toml" "${BACKUP}/cloudkitty.toml"
rm -rf "${BACKUP}/policies"
if [[ -d "${APP}/policies" ]]; then
    rsync -a "${APP}/policies/" "${BACKUP}/policies/"
fi

systemctl stop cloudkitty          # SIGINT: the world takes its final save
cp -a "${APP}/snapshot.json" "${BACKUP}/snapshot.json" 2>/dev/null || true

cp target/release/cloudkitty-server "${APP}/"
# --delete, not cp -r: a merge would leave assets deleted upstream behind, and
# the server would keep serving them.
rsync -a --delete client/ "${APP}/client/"
install -m 644 cloudkitty.toml "${APP}/cloudkitty.toml"
if [[ -d policies ]]; then
    rsync -a --delete policies/ "${APP}/policies/"
fi
chown -R "${SVC_USER}:${SVC_USER}" "$APP"

# `systemctl start` returns as soon as exec succeeds, so give the world a
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
cp -a "${BACKUP}/cloudkitty.toml" "${APP}/cloudkitty.toml"
if [[ -d "${BACKUP}/policies" ]]; then
    rsync -a --delete "${BACKUP}/policies/" "${APP}/policies/"
fi
chown -R "${SVC_USER}:${SVC_USER}" "$APP"
systemctl start cloudkitty || true
sleep 3

if systemctl is-active --quiet cloudkitty; then
    cat >&2 <<MSG

    Rolled back: the previous config and the policy artifacts it names are
    deployed and the world is serving again. The new binary and viewer are
    still in place — ${APP}/cloudkitty.toml and ${APP}/policies were reverted.

    If the new config changes world size, seed, or the roster's kitty ids,
    the saved world cannot resume it. Options:
      - keep the old shape, or
      - start a new world:  cd ${APP} && ./cloudkitty-server --config cloudkitty.toml --fresh
        (--fresh moves the old save to snapshot.json.<timestamp>.bak first)

    The world as of this deploy is saved at ${BACKUP}/snapshot.json.
MSG
else
    cat >&2 <<MSG

    Rollback did not bring it up either. The world as of this deploy is at
    ${BACKUP}/snapshot.json, the previous config at ${BACKUP}/cloudkitty.toml,
    and the artifacts it names at ${BACKUP}/policies.
    Check: journalctl -u cloudkitty -n 50
MSG
fi

exit 1
