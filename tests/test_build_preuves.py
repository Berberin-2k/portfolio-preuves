"""Offline regression tests: publication is never proof of exam validation."""
import datetime as dt
import json
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from build_preuves import PROJECTS, build, title_from_filename


def pdf_bytes() -> bytes:
    # Sufficient to test the PDF signature and EOF guards; not published as a PDF.
    return b"%PDF-1.4\n1 0 obj << /Type /Catalog >> endobj\ntrailer <<>>\n%%EOF\n"


class CatalogueTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.docs = self.root / "docs"
        self.docs.mkdir()
        self.out = self.root / "site"
        self.now = dt.datetime(2026, 11, 10, tzinfo=dt.timezone.utc)

    def tearDown(self):
        self.temp.cleanup()

    def add_pdf(self, relative: str, content: bytes | None = None) -> Path:
        file = self.docs / relative
        file.parent.mkdir(parents=True, exist_ok=True)
        file.write_bytes(pdf_bytes() if content is None else content)
        return file

    def test_empty_repository_outputs_valid_json(self):
        manifest = build(self.root, self.out, now=self.now)
        self.assertEqual(manifest["documents_count"], 0)
        self.assertEqual(manifest["documents"], [])
        self.assertEqual(set(manifest["projects"].keys()), set(PROJECTS.values()))
        self.assertTrue((self.out / "index.html").is_file())
        self.assertTrue((self.out / "preuves.json").is_file())

    def test_two_pdfs_are_grouped_and_links_encoded(self):
        self.add_pdf("U5/glpi/compte-rendu.pdf")
        self.add_pdf("U6/vlan/dossier technique réseau.pdf")
        manifest = build(self.root, self.out, now=self.now)
        self.assertEqual(manifest["documents_count"], 2)
        self.assertEqual(manifest["projects"]["R-GLPI"], 1)
        self.assertEqual(manifest["projects"]["R-VLAN"], 1)
        self.assertEqual(manifest["projects"]["R-VEILLE"], 0)
        glpi = next(x for x in manifest["documents"] if x["realisation"] == "R-GLPI")
        vlan = next(x for x in manifest["documents"] if x["realisation"] == "R-VLAN")
        self.assertEqual(glpi["titre"], "Compte rendu")
        self.assertEqual(glpi["etat"], "Document disponible — à valider")
        self.assertIn("/docs/U6/vlan/dossier%20technique%20r%C3%A9seau.pdf", vlan["url"])
        self.assertEqual(len(glpi["sha256"]), 64)
        self.assertTrue((self.out / "docs/U5/glpi/compte-rendu.pdf").exists())
        self.assertEqual(
            json.loads((self.out / "preuves.json").read_text())["documents_count"], 2
        )

    def test_removed_pdf_disappears_on_next_build(self):
        file = self.add_pdf("U6/infrastructure/procedure.pdf")
        build(self.root, self.out, now=self.now)
        file.unlink()
        manifest = build(self.root, self.out, now=self.now)
        self.assertEqual(manifest["documents"], [])
        self.assertFalse((self.out / "docs/U6/infrastructure/procedure.pdf").exists())

    def test_unknown_project_fails_instead_of_silent_omission(self):
        self.add_pdf("U7/inconnu/compte-rendu.pdf")
        with self.assertRaisesRegex(ValueError, "hors d'un dossier"):
            build(self.root, self.out, now=self.now)

    def test_non_pdf_is_ignored(self):
        file = self.docs / "U5/glpi/note.txt"
        file.parent.mkdir(parents=True)
        file.write_text("not a PDF")
        self.assertEqual(build(self.root, self.out, now=self.now)["documents_count"], 0)

    def test_misnamed_non_pdf_fails(self):
        self.add_pdf("U5/glpi/compte-rendu.pdf", b"not a pdf\n" * 6)
        with self.assertRaisesRegex(ValueError, "sans signature PDF"):
            build(self.root, self.out, now=self.now)

    def test_truncated_pdf_fails(self):
        self.add_pdf("U5/glpi/corrupt.pdf", b"%PDF-1.7\n" + b"x" * 40)
        with self.assertRaisesRegex(ValueError, "incomplet"):
            build(self.root, self.out, now=self.now)

    def test_filename_does_not_decide_validity(self):
        self.assertEqual(title_from_filename("compte-rendu"), "Compte rendu")
        self.assertEqual(title_from_filename("dossier_technique"), "Dossier technique")
        self.assertEqual(title_from_filename("configuration VLAN"), "Configuration VLAN")

    def test_invalid_url_rejected(self):
        with self.assertRaises(ValueError):
            build(self.root, self.out, "http://example.com/docs", now=self.now)

    def test_project_mapping_is_exact(self):
        self.assertEqual(PROJECTS, {
            "U5/glpi": "R-GLPI", "U5/veille": "R-VEILLE",
            "U5/portail": "R-PORTAIL", "U6/vlan": "R-VLAN",
            "U6/infrastructure": "R-INFRA",
        })


if __name__ == "__main__":
    unittest.main()
