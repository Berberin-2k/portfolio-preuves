# Portfolio BTS SIO SISR — Documents et preuves

Ce dépôt public conserve les comptes rendus et dossiers techniques du **Portfolio Projets**. Il génère automatiquement un catalogue `preuves.json` et publie les PDF sur **GitHub Pages**, pour qu'ils soient consultables depuis Framer :

**Portfolio :** https://pooboo.framer.website/projets

> Important : un PDF publié est un **document disponible**, pas une preuve automatiquement validée par un professeur ou un jury. Vérifiez et anonymisez vos fichiers avant de les rendre publics.

## 1. Ajouter un document en 30 secondes

1. Ouvrir le dossier de la réalisation correspondant à votre projet :
   - [U5 · GLPI](docs/U5/glpi)
   - [U5 · Veille](docs/U5/veille)
   - [U5 · Portail documentaire](docs/U5/portail)
   - [U6 · VLAN](docs/U6/vlan)
   - [U6 · Infrastructure](docs/U6/infrastructure)
2. Cliquer sur **Add file → Upload files**.
3. Sélectionner un ou deux PDF (par exemple `compte-rendu.pdf` et `dossier-technique.pdf`), puis **Commit changes** sur `main`.
4. Vérifier le workflow [Publier les preuves PDF](https://github.com/Berberin-2k/portfolio-preuves/actions/workflows/publish-preuves.yml). Il teste les fichiers et publie le nouveau catalogue et les PDF.
5. Ouvrir le [Portfolio Projets](https://pooboo.framer.website/projets) et consulter les preuves de la réalisation correspondante. Le site lit le catalogue à chaque ouverture ; **aucun nouveau Publish Framer n'est nécessaire**.

> Les dossiers sont précréés avec `.gitkeep`. Vous n'avez **pas besoin** de modifier `preuves.json` ou les fichiers Python vous-même.

## 2. Correspondance automatique

| Épreuve | Dossier GitHub | Réalisation Framer |
| --- | --- | --- |
| E5 / U5 | `docs/U5/glpi/` | `R-GLPI` — Déploiement et paramétrage de GLPI |
| E5 / U5 | `docs/U5/veille/` | `R-VEILLE` — Plateforme de veille technologique |
| E5 / U5 | `docs/U5/portail/` | `R-PORTAIL` — Portail documentaire (démo) |
| E6 / U6 | `docs/U6/vlan/` | `R-VLAN` — Conception et déploiement de VLAN |
| E6 / U6 | `docs/U6/infrastructure/` | `R-INFRA` — Services réseau et supervision |

Les noms des fichiers servent de titres par défaut : `compte-rendu.pdf` → **Compte rendu**, `dossier-technique.pdf` → **Dossier technique**. Les PDF avec des espaces ou accents dans le nom sont pris en charge.

**Un dépôt public n'est pas un stockage de fichiers confidentiels.** Avant chaque upload, supprimer ou masquer les noms de clients, identifiants, mots de passe, clés, secrets, coordonnées personnelles et informations internes sensibles.

## 3. Architecture

`Upload PDF → GitHub Actions → validation Python → construction de preuves.json → GitHub Pages → Framer /projets`

- **Script :** [`scripts/build_preuves.py`](scripts/build_preuves.py), sans dépendance externe.
- **Tests :** [`tests/test_build_preuves.py`](tests/test_build_preuves.py).
- **Workflow :** [`.github/workflows/publish-preuves.yml`](.github/workflows/publish-preuves.yml).
- **Catalogue public :** https://berberin-2k.github.io/portfolio-preuves/preuves.json
- **Fichiers PDF publics :** `https://berberin-2k.github.io/portfolio-preuves/docs/U6/vlan/compte-rendu.pdf` (exemple de format d'URL, disponible uniquement si le fichier existe).

Le script ne publie que des PDF reconnaissables (`%PDF-` et marqueur de fin), de taille maximale 25 Mo par fichier, situés dans l'un des cinq dossiers autorisés. Une erreur bloque la publication pour éviter une liste de preuves incomplète ou trompeuse. Les fichiers supprimés du dépôt disparaissent aussi du catalogue après le prochain déploiement.

**Déploiement initial :** dans **Settings → Pages → Build and deployment**, sélectionner **GitHub Actions** comme *Source* (une seule fois), puis relancer le workflow si nécessaire. Cette opération nécessite des droits d'administration sur le dépôt.

## 4. Mettre à jour ou supprimer un PDF

- **Remplacer :** uploader une nouvelle version **avec le même nom et dans le même dossier**.
- **Supprimer :** supprimer le fichier du dépôt et valider le commit.
- **Renommer :** le nom affiché et l'URL changent automatiquement. Les anciens liens ne sont pas conservés.
- **Erreur :** lire l'étape rouge du workflow. Le dernier catalogue GitHub Pages publié reste disponible pendant la correction.

Il peut y avoir un délai de déploiement et de cache après un commit. Framer recharge `preuves.json` à l'ouverture du Portfolio et ne nécessite pas de nouvelle publication.
