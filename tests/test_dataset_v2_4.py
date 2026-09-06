import tempfile
import unittest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

from glyph100_dataset_identity import parent_doc_id_for, parent_split_for  # noqa: E402
from glyph100_dataset_v2_4_build import CandidateIndex, clean_source_text, paragraph_chunks  # noqa: E402


class DatasetV24Tests(unittest.TestCase):
    def test_candidate_selection_keeps_whole_parent_documents(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            index = CandidateIndex(Path(temp_dir) / "candidates.jsonl")
            index.rows = [
                (10, "doc-a:000", "doc-a", 60),
                (10, "doc-a:001", "doc-a", 60),
                (20, "doc-b:000", "doc-b", 80),
            ]

            selected, parents = index.select(target_tokens=100)

        self.assertEqual(selected, {"doc-a:000", "doc-a:001"})
        self.assertEqual(parents, {"doc-a": 120})

    def test_parent_identity_and_split_ignore_chunk_id(self) -> None:
        first = {"id": "book-7:000", "doc_id": "book-7:000", "parent_doc_id": "book-7", "source": "books"}
        second = {"id": "book-7:001", "doc_id": "book-7:001", "parent_doc_id": "book-7", "source": "books"}

        self.assertEqual(parent_doc_id_for(first), "book-7")
        self.assertEqual(parent_doc_id_for(second), "book-7")
        self.assertEqual(parent_split_for(first, 10), parent_split_for(second, 10))

    def test_paragraph_chunks_respect_limit_and_preserve_text(self) -> None:
        text = "\n\n".join(["Ala ma kota i opisuje jego zwyczaje." * 8 for _ in range(12)])

        chunks = paragraph_chunks(text, max_chars=600)

        self.assertGreater(len(chunks), 1)
        self.assertTrue(all(len(chunk) <= 600 for chunk in chunks))
        self.assertEqual("".join(chunks).replace("\n", ""), text.replace("\n", ""))

    def test_wikinews_cleanup_removes_source_and_category_tail(self) -> None:
        text = (
            "To jest właściwa treść artykułu. Zawiera kilka normalnych zdań.\n\n"
            "Źródła\nKategoria:Polska\nhttps://example.invalid"
        )

        cleaned = clean_source_text("wikinews", text)

        self.assertEqual(cleaned, "To jest właściwa treść artykułu. Zawiera kilka normalnych zdań.")
        self.assertNotIn("Kategoria:", cleaned)
        self.assertNotIn("example.invalid", cleaned)


if __name__ == "__main__":
    unittest.main()
