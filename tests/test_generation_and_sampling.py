import tempfile
import types
import unittest
import sys
from pathlib import Path

import numpy as np
import torch

from config import ModelConfig, get_train_config
from model import GPT
from train import TokenDataset, load_checkpoint, save_checkpoint

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from glyph100_dataset_identity import parent_doc_id_for  # noqa: E402


class GenerationTests(unittest.TestCase):
    def test_generate_stops_on_eos(self):
        cfg = ModelConfig(vocab_size=16, context_len=8, d_model=8, n_heads=2, n_layers=1, dropout=0.0)
        model = GPT(cfg)

        def eos_forward(self, idx, targets=None):
            logits = torch.full((idx.size(0), idx.size(1), cfg.vocab_size), -100.0)
            logits[:, -1, 3] = 100.0
            return logits, None

        model.forward = types.MethodType(eos_forward, model)
        prompt = torch.tensor([[7, 8]], dtype=torch.long)
        output = model.generate(prompt, max_new_tokens=6, temperature=0.0, eos_token_id=3)
        self.assertEqual(output.tolist(), [[7, 8, 3]])


class TokenDatasetTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.path = Path(self.temp_dir.name) / "tokens.bin"
        np.arange(81, dtype=np.uint16).tofile(self.path)

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_shuffled_blocks_cover_epoch_without_replacement(self):
        dataset = TokenDataset(str(self.path), block_size=8, sampling="shuffled_blocks", seed=11)
        starts = []
        for _ in range(5):
            x, _ = dataset.get_batch(2, torch.device("cpu"))
            starts.extend(x[:, 0].tolist())
        self.assertEqual(len(starts), dataset.num_blocks)
        self.assertEqual(len(set(starts)), dataset.num_blocks)
        self.assertTrue(all(start % 8 == 0 for start in starts))

    def test_sampler_state_restores_exact_next_batch(self):
        first = TokenDataset(str(self.path), block_size=8, sampling="shuffled_blocks", seed=19)
        first.get_batch(3, torch.device("cpu"))
        state = first.state_dict()
        expected_x, expected_y = first.get_batch(4, torch.device("cpu"))

        resumed = TokenDataset(str(self.path), block_size=8, sampling="shuffled_blocks", seed=19)
        resumed.load_state_dict(state)
        actual_x, actual_y = resumed.get_batch(4, torch.device("cpu"))
        self.assertTrue(torch.equal(expected_x, actual_x))
        self.assertTrue(torch.equal(expected_y, actual_y))

    def test_fixed_validation_panel_is_repeatable_and_side_effect_free(self):
        dataset = TokenDataset(str(self.path), block_size=8, sampling="shuffled_blocks", seed=23)
        state_before = dataset.state_dict()
        first = list(dataset.fixed_eval_batches(2, 3, torch.device("cpu"), seed=29))
        second = list(dataset.fixed_eval_batches(2, 3, torch.device("cpu"), seed=29))
        self.assertEqual(state_before, dataset.state_dict())
        for (x1, y1), (x2, y2) in zip(first, second, strict=True):
            self.assertTrue(torch.equal(x1, x2))
            self.assertTrue(torch.equal(y1, y2))

    def test_glyph100_defaults_to_shuffled_blocks_and_fixed_eval(self):
        cfg = get_train_config("glyph-100m")
        self.assertEqual(cfg.train_sampling, "shuffled_blocks")
        self.assertGreaterEqual(cfg.eval_batches, 32)

    def test_checkpoint_roundtrip_restores_sampler_state(self):
        cfg = get_train_config("glyph-100m")
        cfg.checkpoint_dir = str(Path(self.temp_dir.name) / "checkpoints")
        cfg.tokenizer_path = str(Path(self.temp_dir.name) / "missing-tokenizer.model")
        model_cfg = ModelConfig(vocab_size=16, context_len=8, d_model=8, n_heads=2, n_layers=1, dropout=0.0)
        model = GPT(model_cfg)
        optimizer = torch.optim.AdamW(model.parameters(), lr=1e-4)
        dataset = TokenDataset(str(self.path), block_size=8, sampling="shuffled_blocks", seed=31)
        dataset.get_batch(3, torch.device("cpu"))
        expected_state = dataset.state_dict()

        path = save_checkpoint(
            model,
            optimizer,
            step=7,
            loss=1.25,
            cfg=cfg,
            variant="glyph-100m",
            effective_tokens=64,
            tag="sampler_roundtrip",
            data_state=expected_state,
        )
        restored = TokenDataset(str(self.path), block_size=8, sampling="shuffled_blocks", seed=31)
        load_checkpoint(
            str(path),
            model,
            optimizer,
            expected_variant="glyph-100m",
            expected_model_config=model_cfg,
            dataset=restored,
        )
        self.assertEqual(expected_state, restored.state_dict())


class DocumentIdentityTests(unittest.TestCase):
    def test_chunked_book_uses_shared_parent(self):
        record = {
            "source": "wolne_lektury",
            "source_id": "book-slug#chunk-0042",
            "doc_id": "chunk-hash",
        }
        self.assertEqual(parent_doc_id_for(record), "book-slug")

    def test_constant_dataset_source_id_does_not_merge_web_documents(self):
        record = {
            "source": "fineweb2_pl",
            "source_id": "dataset-name",
            "doc_id": "individual-document-hash",
        }
        self.assertEqual(parent_doc_id_for(record), "individual-document-hash")


if __name__ == "__main__":
    unittest.main()
