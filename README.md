# Wiki Influenceur

Projet de jeu de cartes à collectionner autour des créateurs YouTube, Twitch et autres plateformes : boosters, raretés, collection, puis éventuellement échanges et combats. Nom provisoire.

## État actuel

Socle de publication et page d'attente uniquement. Aucun compte, tirage, paiement, collecte de statistiques ou image de créateur n'est encore implémenté. La stack du jeu reste à choisir.

## Développement et vérification

Node 24 et Git. `npm ci`, puis `npm run build` produit `dist/`, avec le SHA dans `version.json`. La construction contrôle les références aux assets. Pour prévisualiser : `python3 -m http.server 5173 --directory dist`.

La CI GitHub lance le build, la validation Bash et ShellCheck. CodeRabbit est configuré pour des revues en français ; son application GitHub doit avoir accès à ce dépôt.

## Livraison

1. Créer une branche et une PR vers `main`.
2. Attendre la CI et la revue CodeRabbit du dernier commit, traiter ses remarques et résoudre les discussions.
3. Fusionner, puis synchroniser le dépôt local sur `main`.
4. Depuis WSL Ubuntu-26.04 avec Node 24 et l'accès SSH existant : `bash deploy/deploy-vps.sh`.
5. Vérifier la page et `version.json` sur <http://91.134.138.53/wiki-influenceur/>.

Comme PostCompare, le déploiement est une commande explicite après fusion, pas un déploiement automatique GitHub Actions. Aucune clé SSH n'est déposée dans GitHub.

Le script exige un arbre propre correspondant à `origin/main`, construit le site et conserve les versions dans `/opt/wiki-influenceur/releases`. Nginx sert le lien `current`. En cas d'échec de validation, la configuration et la version précédentes sont restaurées. Le script vérifie aussi PostCompare et Palworld.

Sans domaine, le site partage le serveur Nginx de PostCompare via un include dédié dans `/etc/nginx/sites-available/postcompare`. **Un futur déploiement PostCompare remplaçant ce fichier devra conserver cet include**, sinon la route disparaîtra ; relancer le déploiement de ce projet la rétablit. Ne pas exécuter les deux déploiements simultanément. Aucun port ni règle de pare-feu supplémentaire.

Adresse provisoire en HTTP, sans compte ni donnée utilisateur. Domaine et HTTPS à configurer ultérieurement.

## Suite du projet

Définir les règles de boosters et raretés, les créateurs et plateformes couverts, les sources de données autorisées, puis développer la collection et la persistance. Les probabilités et données de démonstration devront être explicites.
