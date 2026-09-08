import tempfile
import types
import unittest
import sys
from pathlib import Path

import numpy as np
import torch

from config import ModelConfig, get_train_config
from model import GPT
from train import (
    TokenDataset,
    get_lr,
    load_checkpoint,
    save_checkpoint,
    validate_resume_contract,
)

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


class SchedulerTests(unittest.TestCase):
    """WSD scheduler (warmup-stable-decay) + cosine regression."""

    MAX_LR = 2e-4
    MIN_LR = 2e-5
    WARMUP = 2000
    DECAY_START = 80566
    DECAY_STEPS = 9700

    def _cfg(self, scheduler_type="wsd", **overrides):
        cfg = get_train_config("glyph-100m")
        cfg.scheduler_type = scheduler_type
        cfg.max_lr = self.MAX_LR
        cfg.min_lr = self.MIN_LR
        cfg.warmup_steps = self.WARMUP
        cfg.decay_start_step = self.DECAY_START
        cfg.decay_steps = self.DECAY_STEPS
        for key, value in overrides.items():
            setattr(cfg, key, value)
        return cfg

    def test_wsd_warmup_ramp(self):
        cfg = self._cfg()
        self.assertEqual(get_lr(0, cfg), 0.0)
        self.assertEqual(get_lr(self.WARMUP, cfg), self.MAX_LR)
        prev = -1.0
        for step in range(0, self.WARMUP + 1, 200):
            lr = get_lr(step, cfg)
            self.assertGreater(lr, prev)
            prev = lr

    def test_wsd_stable_ignores_max_steps(self):
        # open-ended stable: decay_start_step=None must hold max_lr at any
        # step, identically for any max_steps (it must not leak into the
        # WSD formula); step > max_steps must neither fail nor wrap
        for max_steps in (200_000, 1000):
            cfg = self._cfg(max_steps=max_steps, decay_start_step=None)
            self.assertEqual(get_lr(120000, cfg), self.MAX_LR)
        cfg_long = self._cfg(max_steps=200_000, decay_start_step=None)
        cfg_short = self._cfg(max_steps=1000, decay_start_step=None)
        for step in (2001, 40000, 120000):
            self.assertEqual(get_lr(step, cfg_long), get_lr(step, cfg_short))

    def test_wsd_stable_up_to_decay_start(self):
        cfg = self._cfg(max_steps=200_000)
        for step in (2001, 40000, self.DECAY_START - 1, self.DECAY_START):
            self.assertEqual(get_lr(step, cfg), self.MAX_LR)

    def test_wsd_linear_decay_and_clamp(self):
        cfg = self._cfg()
        mid = self.DECAY_START + self.DECAY_STEPS // 2
        self.assertEqual(get_lr(self.DECAY_START, cfg), self.MAX_LR)
        self.assertAlmostEqual(
            get_lr(mid, cfg), (self.MAX_LR + self.MIN_LR) / 2, places=12)
        self.assertAlmostEqual(
            get_lr(self.DECAY_START + self.DECAY_STEPS, cfg), self.MIN_LR,
            places=12)
        prev = self.MAX_LR + 1.0
        for step in range(self.DECAY_START, self.DECAY_START + self.DECAY_STEPS + 1, 733):
            lr = get_lr(step, cfg)
            self.assertLess(lr, prev)
            prev = lr
        # past the decay window: clamp at min_lr, never below
        self.assertEqual(
            get_lr(self.DECAY_START + self.DECAY_STEPS + 5000, cfg), self.MIN_LR)

    def test_wsd_open_ended_stable(self):
        cfg = self._cfg(decay_start_step=None)
        self.assertEqual(get_lr(2001, cfg), self.MAX_LR)
        self.assertEqual(get_lr(10 ** 6, cfg), self.MAX_LR)

    def test_wsd_checkpoint_roundtrip_resume_contract_and_cosine_regression(self):
        import copy

        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        cfg = self._cfg()
        cfg.checkpoint_dir = str(Path(tmp.name) / "checkpoints")
        cfg.tokenizer_path = str(Path(tmp.name) / "missing-tokenizer.model")
        model_cfg = ModelConfig(vocab_size=16, context_len=8, d_model=8, n_heads=2, n_layers=1,
                                dropout=0.0)
        model = GPT(model_cfg)
        optimizer = torch.optim.AdamW(model.parameters(), lr=1e-4)
        path = save_checkpoint(
            model, optimizer, step=100, loss=1.0, cfg=cfg,
            variant="glyph-100m", effective_tokens=64, tag="wsd_roundtrip")
        load_checkpoint(str(path), model, optimizer,
                        expected_variant="glyph-100m",
                        expected_model_config=model_cfg)
        state = torch.load(str(path), map_location="cpu", weights_only=False)
        self.assertEqual(state["scheduler_state"], {
            "type": "wsd", "step": 100, "max_steps": cfg.max_steps,
            "warmup_steps": self.WARMUP, "max_lr": self.MAX_LR,
            "min_lr": self.MIN_LR, "decay_start_step": self.DECAY_START,
            "decay_steps": self.DECAY_STEPS})
        # unchanged config resumes cleanly
        validate_resume_contract(state, cfg, model_cfg, strict=True)
        # changed decay window must STOP without --allow-mismatch ...
        bad = copy.copy(cfg)
        bad.decay_start_step = self.DECAY_START + 1
        with self.assertRaises(ValueError):
            validate_resume_contract(state, bad, model_cfg, strict=True)
        # ... and pass with it
        validate_resume_contract(state, bad, model_cfg, strict=False)
        # changed scheduler type must STOP as well
        bad_type = copy.copy(cfg)
        bad_type.scheduler_type = "cosine"
        with self.assertRaises(ValueError):
            validate_resume_contract(state, bad_type, model_cfg, strict=True)
        # cosine regression: v2.4.2 log value at step 15000
        cos = self._cfg(scheduler_type="cosine", max_steps=200_000)
        self.assertAlmostEqual(get_lr(15000, cos), 1.981e-4, places=7)


if __name__ == "__main__":
    unittest.main()
