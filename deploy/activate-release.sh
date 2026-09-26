#!/usr/bin/env bash
set -euo pipefail
release=${1:?Release required}
commit=${2:?Commit required}
[[ "$release" =~ ^[0-9]{8}T[0-9]{6}Z-[a-f0-9]{12}$ ]]
[[ "$commit" =~ ^[a-f0-9]{40}$ ]]
upload="/home/ubuntu/wiki-influenceur-upload/$release"
base=/opt/wiki-influenceur
host_config=/etc/nginx/sites-available/postcompare
snippet=/etc/nginx/snippets/wiki-influenceur.conf
install -d -m 755 "$base/releases"
exec 9>"$base/deploy.lock"
flock -n 9
[[ ! -e "$base/releases/$release" ]]
[[ -f "$upload/site/index.html" && -f "$upload/site/style.css" ]]
grep -Fq "$commit" "$upload/site/version.json"
backup="$base/releases/$release-backup"
install -d -m 700 "$backup"
cp "$host_config" "$backup/host.conf"
if [[ -f "$snippet" ]]; then cp "$snippet" "$backup/snippet.conf"; fi
previous=$(readlink "$base/current" || true)
rollback() {
    trap - ERR
    cp "$backup/host.conf" "$host_config"
    if [[ -f "$backup/snippet.conf" ]]; then
        cp "$backup/snippet.conf" "$snippet"
    else
        rm -f "$snippet"
    fi
    if [[ -n "$previous" ]]; then
        ln -sfn "$previous" "$base/current"
    else
        rm -f "$base/current"
    fi
    nginx -t && systemctl reload nginx
    echo 'Deployment failed; previous configuration restored.' >&2
}
trap rollback ERR
install -d -m 755 "$base/releases/$release"
install -m 644 "$upload/site/"* "$base/releases/$release/"
install -m 644 "$upload/location.conf" "$snippet"
# Add only our include to the existing IP virtual host; preserve its other routes.
python3 - "$host_config" <<'PY'
import pathlib, sys
path = pathlib.Path(sys.argv[1])
text = path.read_text()
include = '    include /etc/nginx/snippets/wiki-influenceur.conf;'
anchor = '    server_name 91.134.138.53;'
if include not in text:
    if text.count(anchor) != 1:
        raise SystemExit('Expected exactly one IP virtual host; refusing to edit')
    path.write_text(text.replace(anchor, anchor + '\n' + include))
PY
ln -sfn "$base/releases/$release" "$base/current"
nginx -t
systemctl reload nginx
ready=false
for attempt in $(seq 1 10); do
    if curl -fsS -H 'Host: 91.134.138.53' http://127.0.0.1/wiki-influenceur/version.json | grep -Fq "$commit"; then
        ready=true
        break
    fi
    sleep 1
done
[[ "$ready" == true ]]
curl -fsS -H 'Host: 91.134.138.53' http://127.0.0.1/ | grep -q PostCompare
systemctl is-active postcompare nginx palworld-bot
trap - ERR
echo "Activated $release; previous: ${previous:-none}"
