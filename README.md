# kasalma-site

Site public de Kasalma, hébergé sur **GitHub Pages**. Pour l'instant : accueil minimal, conditions d'utilisation (`/cgu/`) et politique de confidentialité (`/confidentialite/`), les deux URL à donner à l'App Store et à Google Play.

HTML + CSS statique, sans build. Couleurs et typo reprises du handoff design (`../design-handoff/.../tokens`). Police Nunito servie par le site (licence OFL dans `assets/fonts/OFL.txt`), pour n'appeler aucun service tiers.

## Aperçu local

```sh
python3 -m http.server 4000   # puis http://localhost:4000
```

## Mise en ligne

1. Créer le dépôt sur GitHub (ex. `kasalma-site`), puis :
   `git remote add origin git@github.com:<compte>/kasalma-site.git && git push -u origin main`
2. Sur GitHub : Settings > Pages > Source « Deploy from a branch », branche `main`, dossier `/ (root)`.
3. Domaine `kasalma.com` (facultatif) : ajouter un fichier `CNAME` contenant `kasalma.com`, puis côté DNS des enregistrements `A` vers 185.199.108.153, .109.153, .110.153, .111.153 (et `www` en CNAME vers `<compte>.github.io`). Cocher « Enforce HTTPS ».

Les pages utilisent des liens relatifs, donc elles marchent aussi à l'adresse `<compte>.github.io/kasalma-site/`. Seule la page 404 suppose le domaine à la racine.

## À compléter avant publication

Les trous sont surlignés dans les pages (classe `todo`) :

- **Éditeur** : nom, statut juridique, adresse, SIRET, directeur de la publication (CGU § 1, confidentialité § 1).
- **Service d'envoi d'e-mails** (codes de connexion, invitations) : nom et pays (confidentialité § 6).
- **Médiateur de la consommation** : obligatoire pour vendre à des particuliers (CGU § 15).
- Créer l'adresse **contact@kasalma.com** (utilisée partout).
- Si un outil de gestion d'abonnements est ajouté (ex. RevenueCat) ou un suivi d'erreurs (ex. Sentry), l'ajouter au tableau des prestataires.

Les textes décrivent la v1 prévue dans `../cadrage-v1.md` (compte, tribu, synchro, notifications, lien d'agenda, premium). À relire à chaque nouvelle fonction qui touche aux données. Ce ne sont pas des textes validés par un juriste.
