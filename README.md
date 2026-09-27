# Wiki Influenceur

Futur jeu de cartes de créateurs YouTube/Twitch et autres plateformes. État actuel : page d'attente et infrastructure CI/CD ; le jeu reste à développer.

## Pipeline automatique

1. Branche et PR : build, tests du déploiement, ShellCheck et revue CodeRabbit.
2. `main` exige une PR, les contrôles requis verts et les discussions résolues, sans contournement administrateur. Traiter les remarques avant fusion.
3. Après fusion par squash, GitHub Actions construit et teste le commit de `main`, puis transfère cet artefact sur le VPS.
4. Le serveur vérifie le SHA, active atomiquement la version et vérifie la réponse HTTP. Un échec restaure le lien précédent.

La fusion reste explicite. Aucun déploiement depuis une PR. Adresse : http://91.134.138.53/wiki-influenceur/ ; `version.json` identifie le commit servi.

## Local

Node 24 : `npm ci && npm run build`. Prévisualisation : `python3 -m http.server 5173 --directory dist`. Sous WSL : `python3 -m unittest discover -s deploy -p 'test_*.py'` et `shellcheck deploy/*.sh`.

## Réutiliser pour un autre projet

`.github/workflows/ci.yml` accepte `workflow_call`, avec `node-version`, `java-version` et `verify-command`. Exemple React/Java :

```yaml
name: CI
on: [push, pull_request]
permissions:
  contents: read
  pull-requests: read
jobs:
  checks:
    uses: LudovicDespaux/wiki_influenceur/.github/workflows/ci.yml@main
    with:
      node-version: '24'
      java-version: '17'
      verify-command: 'cd frontend && npm ci && npm run build && cd ../backend && mvn -B verify'
```

Remplacer `@main` par un SHA validé pour figer la version. Le contrôle requis du dépôt appelant doit correspondre au nom réellement produit. CodeRabbit et les règles GitHub restent propres à chaque dépôt. Laisser `DEPLOY_ENABLED` absent pour utiliser seulement la CI.

`.github/workflows/deploy-reusable.yml` accepte un artefact de site statique, un hôte, un utilisateur et une URL publique. Il reçoit une clé SSH dédiée et les clés d'hôte vérifiées. Un serveur Java comme PostCompare nécessitera un adaptateur de réception et de redémarrage systemd : ne pas envoyer son JAR au récepteur statique.

## Infrastructure

Variables GitHub : `DEPLOY_ENABLED`, `DEPLOY_HOST`, `DEPLOY_USER`, `PUBLIC_URL`. Secrets : `DEPLOY_SSH_KEY`, `DEPLOY_KNOWN_HOSTS`. Environnement `production` limité à `main`.

Le compte VPS `wiki-deploy` n'a pas de sudo. Sa clé est restreinte à `/usr/local/libexec/wiki-influenceur-receive.py`, installé et modifiable par root uniquement. Il accepte des fichiers statiques, refuse les liens et chemins sortant du dossier, et n'exécute jamais les fichiers reçus. Le récepteur vérifie que le commit est le `main` courant de ce dépôt. Pour un autre projet, adapter cette référence, l'URL et le dossier côté serveur, avec un compte et une clé distincts.

Versions : `/opt/wiki-influenceur/releases` ; lien actif : `current`. Les tests vérifient notamment le rejet des traversées de chemins, des liens symboliques et des SHA incohérents. La rétention des versions VPS reste manuelle ; les artefacts GitHub expirent après un jour.

Le site partage temporairement le virtual host Nginx de PostCompare via `/etc/nginx/snippets/wiki-influenceur.conf`. Un déploiement PostCompare qui remplace son fichier Nginx doit conserver cet include. Domaine et HTTPS seront ajoutés ultérieurement.

`deploy/deploy-vps.sh` et `activate-release.sh` constituent un secours administrateur explicite. Ils nécessitent l'accès SSH administrateur existant ; après usage, vérifier que `deploy.lock` appartient encore à `wiki-deploy`.

## Gratuité

Les runners standards GitHub sont gratuits pour les dépôts publics ; les dépôts privés ont des quotas. Aucun service payant supplémentaire souscrit. CodeRabbit dépend séparément des droits et de l'offre du compte.
