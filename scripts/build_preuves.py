#!/usr/bin/env python3
"""Build the public PDF evidence catalogue used by the Framer Projects page.

No credentials, LLM, network access or human approval is required.
PDFs are considered *available*, not automatically validated as exam evidence.
"""
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import re
import shutil
import unicodedata
from pathlib import Path
from urllib.parse import quote, urlsplit

ROOT = Path(__file__).resolve().parents[1]
MAX_PDF_BYTES = 25 * 1024 * 1024
SCHEMA_VERSION = 1

# These identifiers must match MatriceCompetencesDemo.tsx on Framer.
PROJECTS: dict[str, str] = {
    "U5/glpi": "R-GLPI",
    "U5/veille": "R-VEILLE",
    "U5/portail": "R-PORTAIL",
    "U6/vlan": "R-VLAN",
    "U6/infrastructure": "R-INFRA",
}
SYNTHESIS_DIR = "U5/tableau-de-synthese"
SYNTHESIS_ID = "U5-SYNTHESE"
DEFAULT_BASE_URL = "https://berberin-2k.github.io/portfolio-preuves"
TITLE_MAP = {
    "compte rendu": "Compte rendu",
    "tableau de synthese": "Tableau de synthèse",
    "dossier technique": "Dossier technique",
    "rapport": "Rapport",
    "documentation": "Documentation",
    "procedure": "Procédure",
    "schema": "Schéma technique",
    "tests": "Tests et validation",
    "recette": "Recette et validation",
}


def title_from_filename(stem: str) -> str:
    spaced = re.sub(r"[-_.]+", " ", stem).strip()
    spaced = re.sub(r"\s+", " ", spaced)
    normalized = unicodedata.normalize("NFKD", spaced.casefold())
    normalized = "".join(ch for ch in normalized if not unicodedata.combining(ch))
    if normalized in TITLE_MAP:
        return TITLE_MAP[normalized]
    return spaced[:1].upper() + spaced[1:] if spaced else "Document PDF"


def validate_pdf(path: Path) -> int:
    if path.is_symlink():
        raise ValueError(f"Les liens symboliques sont interdits : {path}")
    if len(path.name) > 140 or path.name.startswith("."):
        raise ValueError(f"Nom du fichier PDF non accepté : {path.name}")
    size = path.stat().st_size
    if not 20 <= size <= MAX_PDF_BYTES:
        raise ValueError(f"PDF vide, trop petit ou > 25 Mo : {path}")
    with path.open("rb") as f:
        if f.read(5) != b"%PDF-":
            raise ValueError(f"Fichier sans signature PDF : {path}")
        f.seek(max(0, size - 4096))
        if b"%%EOF" not in f.read():
            raise ValueError(f"PDF incomplet (fin de fichier introuvable) : {path}")
    return size


def valid_base_url(value: str) -> str:
    result = urlsplit(value.strip())
    if result.scheme != "https" or not result.hostname or result.query or result.fragment:
        raise ValueError("Base URL must be a full HTTPS URL without query or fragment")
    return value.strip().rstrip("/")


def build(root: Path, output: Path, base_url: str = DEFAULT_BASE_URL, now: dt.datetime | None = None) -> dict:
    root = root.resolve()
    docs = root / "docs"
    output = output.resolve()
    base_url = valid_base_url(base_url)
    stamp = (now or dt.datetime.now(dt.timezone.utc)).astimezone(dt.timezone.utc)
    if not docs.is_dir():
        raise ValueError("Le dossier docs/ n'existe pas")

    # Reject misplaced PDFs: silently ignoring an uploaded file would be confusing.
    all_pdfs = sorted(docs.rglob("*"), key=lambda p: p.as_posix().casefold())
    actual_files = [p for p in all_pdfs if p.is_file() and p.suffix.lower() == ".pdf"]
    documents = []
    tableaux_synthese_u5 = []
    seen_names: set[str] = set()
    copies: list[tuple[Path, Path]] = []

    for file in actual_files:
        rel = file.relative_to(docs)
        folder = rel.parent.as_posix()
        is_synthesis = folder == SYNTHESIS_DIR
        if folder not in PROJECTS and not is_synthesis:
            raise ValueError(f"PDF hors d'un dossier de projet reconnu : docs/{rel.as_posix()}")
        size = validate_pdf(file)
        rel_public = Path("docs") / rel
        url_path = "/".join(quote(part, safe="") for part in rel_public.parts)
        document_url = base_url + "/" + url_path
        key = rel_public.as_posix().casefold()
        if key in seen_names:
            raise ValueError(f"Chemin PDF en double (casse) : {rel_public}")
        seen_names.add(key)
        digest = hashlib.sha256(file.read_bytes()).hexdigest()
        stable_id = hashlib.sha256(rel_public.as_posix().encode("utf-8")).hexdigest()[:12].upper()
        project = SYNTHESIS_ID if is_synthesis else PROJECTS[folder]
        record = {
            "id": f"AUTO-{stable_id}",
            "realisation": project,
            "titre": title_from_filename(file.stem),
            "type": "Document PDF",
            "format": "PDF",
            "etat": "Document disponible — à valider",
            "objet": "Document hébergé dans le dépôt public GitHub du portfolio.",
            "attendu": "Consulter le PDF et vérifier qu'il correspond à la réalisation et aux compétences revendiquées.",
            "url": document_url,
            "source_path": rel_public.as_posix(),
            "size_bytes": size,
            "sha256": digest,
        }
        if is_synthesis:
            tableaux_synthese_u5.append(record)
        else:
            documents.append(record)
        copies.append((file, output / rel_public))

    # Generate only after all uploads have passed validation.
    previous_docs = output / "docs"
    if previous_docs.exists():
        shutil.rmtree(previous_docs)
    output.mkdir(parents=True, exist_ok=True)
    for src, dest in copies:
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dest)

    manifest = {
        "schema_version": SCHEMA_VERSION,
        "generated_at": stamp.isoformat().replace("+00:00", "Z"),
        "publication": "GitHub Pages",
        "repository": "Berberin-2k/portfolio-preuves",
        "documents_count": len(documents),
        "tableau_synthese_u5_count": len(tableaux_synthese_u5),
        "tableau_synthese_u5": tableaux_synthese_u5,
        "projects": {value: sum(d["realisation"] == value for d in documents)
                     for value in PROJECTS.values()},
        "documents": documents,
    }
    (output / "preuves.json").write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    (output / ".nojekyll").write_text("", encoding="utf-8")
    (output / "index.html").write_text(
        '<!doctype html><html lang="fr"><meta charset="utf-8">'
        '<title>Documents du Portfolio BTS SIO</title>'
        '<meta name="viewport" content="width=device-width,initial-scale=1">'
        '<main style="font:16px system-ui;margin:10vh auto;max-width:45rem;padding:2rem">'
        '<h1>Portfolio BTS SIO — documents</h1><p>Catalogue public des documents PDF.</p>'
        '<p><a href="preuves.json">Ouvrir le catalogue JSON</a></p></main></html>\n',
        encoding="utf-8"
    )
    return manifest


def main() -> None:
    parser = argparse.ArgumentParser(description="Build the static portfolio PDF index")
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--output", type=Path, default=ROOT / "site")
    parser.add_argument("--base-url", default=DEFAULT_BASE_URL)
    args = parser.parse_args()
    manifest = build(args.root, args.output, args.base_url)
    print(f"[OK] {manifest['documents_count']} PDF(s) de projet et {manifest['tableau_synthese_u5_count']} tableau(x) de synthèse U5")
    print("Projet(s) : " + ", ".join(f"{key}={count}" for key, count in manifest["projects"].items()))


if __name__ == "__main__":
    main()
