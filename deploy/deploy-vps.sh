#!/usr/bin/env bash
set -euo pipefail
root=$(cd "$(dirname "$0")/.." && pwd)
cd "$root"
[[ -z $(git status --porcelain) ]] || { echo 'Commit changes before deploying.' >&2; exit 1; }
git fetch origin main
commit=$(git rev-parse HEAD)
[[ "$commit" == "$(git rev-parse origin/main)" ]] || { echo 'Deploy only the merged origin/main commit.' >&2; exit 1; }
npm ci
npm run build
release="$(date -u +%Y%m%dT%H%M%SZ)-${commit:0:12}"
vps=ubuntu@91.134.138.53
upload="/home/ubuntu/wiki-influenceur-upload/$release"
ssh -o BatchMode=yes "$vps" "mkdir -p '$upload/site'"
scp -r dist/. "$vps:$upload/site/"
scp deploy/activate-release.sh deploy/location.conf "$vps:$upload/"
ssh -o BatchMode=yes "$vps" "sudo -n bash '$upload/activate-release.sh' '$release' '$commit'"
curl --fail --silent --show-error http://91.134.138.53/wiki-influenceur/version.json | grep -F "$commit"
