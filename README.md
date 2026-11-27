# kasalma-site

Site public de Kasalma (kasalma.com), hébergé sur **GitHub Pages**. Il contient la page d'accueil avec la liste d'attente, les conditions d'utilisation (`/fr/cgu/`) et la politique de confidentialité (`/fr/confidentialite/`). Ces deux dernières adresses sont celles à donner à l'App Store et à Google Play.

| Dossier | Contenu |
|---|---|
| `docs/` | **le site publié** : HTML + CSS statique, sans build. Les couleurs et la typo viennent du handoff design ; Nunito est servie par le site. |
| `tools/` | suivi des chiffres, repris de PokerPerf : collecte, rapport mensuel, IndexNow, image de partage. Ce dossier n'est pas publié. |
| `seo/` | les mots-clés à faire mesurer dans Google Keyword Planner. |

## Aperçu local

```sh
cd docs && python3 -m http.server 8000   # puis http://localhost:8000
```

## Mise en ligne (à faire par Rémy)

1. **GitHub** : créer le dépôt `kasalma-site`, puis `git remote add origin git@github.com:<compte>/kasalma-site.git && git push -u origin main`.
2. **Pages** : Settings > Pages > « Deploy from a branch », branche `main`, dossier **`/docs`**. Le fichier `docs/CNAME` déclare déjà `kasalma.com`.
3. **DNS chez OVH** (kasalma.com pointe aujourd'hui sur la page de parking OVH) :
   - enregistrements `A` de `kasalma.com` vers 185.199.108.153, 185.199.109.153, 185.199.110.153 et 185.199.111.153, en supprimant l'`A` actuel 213.186.33.5 ;
   - `www` en `CNAME` vers `<compte>.github.io.` ;
   - une fois le certificat émis, cocher « Enforce HTTPS » dans Pages.
4. **Liste d'attente** : créer un formulaire « Kasalma » dans Formspree (même compte que PokerPerf), puis remplacer `FORMSPREE_ID` par son identifiant dans `docs/index.html` (2 formulaires).
5. **Mesure d'audience** : dans Cloudflare, Web Analytics > Add a site > `kasalma.com`. Coller le jeton du beacon dans `CF_BEACON_TOKEN` (`docs/assets/site.js`). La mesure ne tourne que sur kasalma.com, jamais en local.
6. **Search Console** : ajouter la propriété de domaine `kasalma.com` (vérification par enregistrement TXT chez OVH), puis soumettre `https://kasalma.com/sitemap.xml`. Dans Bing Webmaster Tools, importer depuis Search Console.
7. **Brancher le rapport mensuel** : créer `~/.config/kasalma-report/config.json` :
   ```json
   {"gsc_site": "sc-domain:kasalma.com", "cf_site_tag": "<siteTag Cloudflare>", "formspree_form": "<id>"}
   ```
   Le `siteTag` n'est pas le jeton du beacon : il apparaît dans l'URL de la page Web Analytics du site. La clé API Formspree, facultative, va dans `~/.config/kasalma-report/formspree_key` (sinon le nombre d'inscrits est à lire dans Formspree).

## Suivi des chiffres (`tools/`)

Les identifiants viennent de PokerPerf : même compte Google (`~/.config/pokerperf-gsc/`) et même compte Cloudflare (`~/.config/pokerperf-cf/`). Rien de secret n'est dans le dépôt.

- `python3 -I tools/collect.py` affiche les chiffres de Search Console (28 derniers jours comparés aux 28 précédents), de Cloudflare et le nombre d'inscrits (total, Android/iPhone, formulaire du haut ou du bas). Il ne garde jamais les adresses e-mail.
- **Rapport mensuel** : le cron `45 6 1 * *` lance `tools/run-rapport.sh`, qui collecte les chiffres, demande l'analyse à Claude, puis envoie l'e-mail « Rapport Kasalma » à Rémy seulement (garde-fou `tools/guard-send.py`). Le script ne fait rien tant que le fichier `config.json` n'existe pas. Les instantanés sont rangés dans `~/.local/share/kasalma-report/`.
- **IndexNow** : après chaque push, une fois la page publiée, lancer `python3 -I tools/indexnow.py --since <ancien HEAD>`. Cela prévient Bing (donc aussi ChatGPT Search, Copilot et DuckDuckGo). La clé publique est `docs/<clé>.txt`.
- **Image de partage** : gabarit `tools/og/og-cover.html`, rendu avec `chrome --headless=new --window-size=1200,630 --screenshot=docs/assets/img/og-cover.png file://$PWD/tools/og/og-cover.html`.

## À compléter avant publication

Les trous sont surlignés dans les pages (classe `todo`) :

- **Éditeur** : nom, statut juridique, adresse, SIRET, directeur de la publication (CGU § 1, confidentialité § 1).
- **Service d'envoi d'e-mails** (codes de connexion, invitations) : nom et pays (confidentialité § 6).
- **Médiateur de la consommation** : obligatoire pour vendre à des particuliers (CGU § 15).
- Créer l'adresse **contact@kasalma.com**, utilisée partout.
- Ajouter au tableau des prestataires tout nouvel outil : gestion d'abonnements (RevenueCat…), suivi d'erreurs (Sentry…).

Les textes légaux décrivent la v1 prévue dans `../cadrage-v1.md`. Il faut les relire à chaque nouvelle fonction qui touche aux données. Aucun juriste ne les a validés.
