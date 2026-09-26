import { cpSync, existsSync, mkdirSync, readFileSync, writeFileSync } from 'node:fs';
import { execFileSync } from 'node:child_process';
import assert from 'node:assert/strict';
const html = readFileSync('site/index.html', 'utf8');
assert.match(html, /<html lang="fr">/);
assert.match(html, /Wiki Influenceur/);
for (const [, path] of html.matchAll(/(?:src|href)="([^"#:]+)"/g)) {
  if (!path.startsWith('https://')) assert.ok(existsSync(`site/${path}`), `Missing asset: ${path}`);
}
mkdirSync('dist', { recursive: true });
cpSync('site', 'dist', { recursive: true });
const commit = execFileSync('git', ['rev-parse', 'HEAD'], { encoding: 'utf8' }).trim();
writeFileSync('dist/version.json', JSON.stringify({ commit }) + '\n');
console.log(`Built ${commit}`);
