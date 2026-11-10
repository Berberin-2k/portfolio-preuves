# Portfolio BTS SIO SISR — Documents et preuves

Ce dépôt public conserve les comptes rendus, dossiers techniques, certifications et le CV du **Portfolio BTS SIO SISR**. Il génère automatiquement un catalogue `preuves.json` et publie les PDF sur **GitHub Pages**, pour qu'ils soient consultables depuis Framer :

**Portfolio :** https://pooboo.framer.website/projets

> Important : un PDF publié est un **document disponible**, pas une preuve automatiquement validée par un professeur ou un jury. Vérifiez et anonymisez vos fichiers avant de les rendre publics.

## 1. Ajouter un document en 30 secondes

1. Ouvrir le dossier de la réalisation correspondant à votre projet :
   - [Certifications · attestations et certificats](docs/certifications)
   - [CV · curriculum vitae](docs/cv)
   - [U5 · Tableau de synthèse](docs/U5/tableau-de-synthese) — document transversal E5/U5, indépendant des projets.
   - [U5 · GLPI](docs/U5/glpi)
   - [U5 · Veille](docs/U5/veille)
   - [U5 · Portail documentaire](docs/U5/portail)
   - [U6 · VLAN](docs/U6/vlan)
   - [U6 · Infrastructure](docs/U6/infrastructure)
2. Cliquer sur **Add file → Upload files**.
3. Sélectionner un ou deux PDF (par exemple `compte-rendu.pdf` et `dossier-technique.pdf`), puis **Commit changes** sur `main`.
4. Vérifier le workflow [Publier les preuves PDF](https://github.com/Berberin-2k/portfolio-preuves/actions/workflows/publish-preuves.yml). Il teste les fichiers et publie le nouveau catalogue et les PDF.
5. Ouvrir la page correspondante : [Projets](https://pooboo.framer.website/projets), [Certifications](https://pooboo.framer.website/certifications) ou [Profil](https://pooboo.framer.website/topics/profil). Le site lit le catalogue à chaque ouverture ; **aucun nouveau Publish Framer n'est nécessaire**.

> Les dossiers sont précréés avec `.gitkeep`. Vous n'avez **pas besoin** de modifier `preuves.json` ou les fichiers Python vous-même.

## 2. Correspondance automatique

| Épreuve | Dossier GitHub | Réalisation Framer |
| --- | --- | --- |
| E5 / U5 | `docs/U5/glpi/` | `R-GLPI` — Déploiement et paramétrage de GLPI |
| E5 / U5 | `docs/U5/veille/` | `R-VEILLE` — Plateforme de veille technologique |
| E5 / U5 | `docs/U5/portail/` | `R-PORTAIL` — Portail documentaire (démo) |
| E6 / U6 | `docs/U6/vlan/` | `R-VLAN` — Conception et déploiement de VLAN |
| E6 / U6 | `docs/U6/infrastructure/` | `R-INFRA` — Services réseau et supervision |

**Tableau de synthèse E5/U5 :** placez votre PDF dans `docs/U5/tableau-de-synthese/` (nom conseillé : `tableau-de-synthese.pdf`). Ce document se montre directement **au-dessus de la matrice** lorsque le lecteur choisit **U5**, sans être rattaché à un projet particulier. Le catalogue public conserve une liste séparée `tableau_synthese_u5`; la page Framer la lit automatiquement sans Publish manuel. Ne placez pas ce PDF dans `docs/U5/glpi/`, `docs/U5/veille/` ou `docs/U5/portail/`.

Les noms des fichiers servent de titres par défaut : `compte-rendu.pdf` → **Compte rendu**, `dossier-technique.pdf` → **Dossier technique**. Les PDF avec des espaces ou accents dans le nom sont pris en charge.

**Un dépôt public n'est pas un stockage de fichiers confidentiels.** Avant chaque upload, supprimer ou masquer les noms de clients, identifiants, mots de passe, clés, secrets, coordonnées personnelles et informations internes sensibles.

## 3. CV et certifications — synchronisation automatique

### Ajouter une certification

1. Ouvrir [`docs/certifications/`](docs/certifications) et cliquer sur **Add file → Upload files**.
2. Ajouter le PDF directement dans ce dossier, par exemple `Certification-Cisco.pdf` ou `Attestation-Linux.pdf`.
3. Valider le commit sur `main`. GitHub Actions détecte le PDF, valide sa structure et publie son URL dans `preuves.json → certifications[]`.
4. La page [Certifications](https://pooboo.framer.website/certifications) affiche automatiquement une carte par fichier avec lien PDF en nouvel onglet.

Le **nom du fichier sert de titre**. L'organisme de délivrance, la date et la validité ne sont pas déduits automatiquement : un PDF publié n'est pas une confirmation de validité.

### Ajouter ou remplacer le CV

1. Ouvrir [`docs/cv/`](docs/cv).
2. Uploader **exactement `cv.pdf`**. Le nom fixe garantit que le bouton CV de la page Profil conserve toujours le même lien public.
3. Valider le commit. Le catalogue public expose `preuves.json → cv` et le bouton **Mon CV** sur [Profil](https://pooboo.framer.website/topics/profil) devient cliquable : il ouvre `https://berberin-2k.github.io/portfolio-preuves/docs/cv/cv.pdf` en nouvel onglet.
4. Pour une nouvelle version, remplacer `cv.pdf` dans le même dossier. En cas de suppression, le bouton CV redevient inactif lors de la prochaine consultation du catalogue.

**Ne publiez pas** d'adresse personnelle, de numéro de téléphone privé non destiné au public ou de données sensibles non nécessaires. Ce dépôt est **Public** ; les PDF pourront être téléchargés par toute personne connaissant l'URL.

## 4. Architecture

`Upload PDF → GitHub Actions → validation Python → construction de preuves.json → GitHub Pages → Framer /projets`

- **Script :** [`scripts/build_preuves.py`](scripts/build_preuves.py), sans dépendance externe.
- **Tests :** [`tests/test_build_preuves.py`](tests/test_build_preuves.py).
- **Workflow :** [`.github/workflows/publish-preuves.yml`](.github/workflows/publish-preuves.yml).
- **Catalogue public :** https://berberin-2k.github.io/portfolio-preuves/preuves.json
- **Fichiers PDF publics :** `https://berberin-2k.github.io/portfolio-preuves/docs/U6/vlan/compte-rendu.pdf` (exemple de format d'URL, disponible uniquement si le fichier existe).

Le manifeste `preuves.json` contient maintenant quatre groupes indépendants : `documents` (PDF liés aux réalisations), `tableau_synthese_u5` (documents transversaux U5), `certifications` (certificats et attestations) et `cv` (un seul PDF ou `null`). Tous sont publiés par le même workflow GitHub Actions.

Le script ne publie que des PDF reconnaissables (`%PDF-` et marqueur de fin), de taille maximale 25 Mo par fichier, situés dans l'un des cinq dossiers de projets autorisés ou dans `docs/U5/tableau-de-synthese/`, `docs/certifications/` ou `docs/cv/`. Une erreur bloque la publication pour éviter une liste de preuves incomplète ou trompeuse. Les fichiers supprimés du dépôt disparaissent aussi du catalogue après le prochain déploiement.

**Déploiement initial :** dans **Settings → Pages → Build and deployment**, sélectionner **GitHub Actions** comme *Source* (une seule fois), puis relancer le workflow si nécessaire. Cette opération nécessite des droits d'administration sur le dépôt.

## 5. Mettre à jour ou supprimer un PDF

- **Remplacer :** uploader une nouvelle version **avec le même nom et dans le même dossier**.
- **Supprimer :** supprimer le fichier du dépôt et valider le commit.
- **Renommer :** le nom affiché et l'URL changent automatiquement. Les anciens liens ne sont pas conservés.
- **Erreur :** lire l'étape rouge du workflow. Le dernier catalogue GitHub Pages publié reste disponible pendant la correction.

Il peut y avoir un délai de déploiement et de cache après un commit. Framer recharge `preuves.json` à l'ouverture du Portfolio et ne nécessite pas de nouvelle publication.
