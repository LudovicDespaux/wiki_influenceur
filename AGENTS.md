# Travail sur Wiki Influenceur

- Ce dépôt contient actuellement le socle de publication, pas encore le jeu.
- Lire README.md et les scripts deploy/ avant toute livraison.
- Ne jamais pousser directement sur main : branche, PR, CI verify verte et revue CodeRabbit du dernier SHA. Examiner et corriger les remarques avant fusion ; ne pas assimiler un accusé de réception à une revue.
- Fusion par squash après revue : GitHub Actions publie automatiquement main. Suivre le workflow et vérifier la version publique. Ne pas doubler cette publication par un déploiement manuel.
- Ne pas désactiver les protections pour débloquer une fusion.
- Préserver PostCompare, Palworld, les clés SSH et les données des autres projets du VPS. Ne pas lancer de durcissement système ou modifier le pare-feu pour une livraison.
- Vérifier la page publique et version.json, et annoncer précisément ce qui a été testé et déployé.
- Le site utilise temporairement /wiki-influenceur/ sur le serveur Nginx de PostCompare. Préserver l'include dédié lors de toute modification de ce virtual host.
- Ne jamais commiter de secrets ou de données personnelles. Les futures cartes de démonstration et leurs statistiques doivent être clairement identifiées.
