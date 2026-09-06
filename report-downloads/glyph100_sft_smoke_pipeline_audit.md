# Glyph-100M SFT smoke pipeline audit

## Verdict

C: SFT pipeline has a labels/mask off-by-one bug; do not run larger SFT or tiny overfit until fixed and re-audited.

## Critical Finding

`SFTDataset._make_pair` masks with `i <= assistant_pos`. For causal LM, `y[assistant_pos]` is the first token after `<|assistant|>`, so this masks the first response token. That is a real labels/mask bug.

## Training Template

```text
<|user|>
{instruction}
<|assistant|>
{response}
<|end|>

```

### Training Template Example 1
```text
<|user|>
Nie rozwijaj bez końca: dlaczego warto mierzyć loss? Jednym zdaniem.
<|assistant|>
Loss pokazuje, czy model uczy się przewidywać dane treningowe lub walidacyjne.
<|end|>
```

### Training Template Example 2
```text
<|user|>
Popraw tekst: Projekt może być ciekawy, ale obecnie ma zbyt wiele funkcji planowanych na start.
<|assistant|>
Projekt jest ciekawy, ale ma zbyt szeroki zakres na start.
<|end|>
```

### Training Template Example 3
```text
<|user|>
Czy ta diagnoza jest pewna? Wskaż ograniczenie.
<|assistant|>
Nie. Bez pełnych danych można mówić tylko o najbardziej prawdopodobnym wyjaśnieniu.
<|end|>
```

## Eval Generation Prompt

```text
<|user|>
{prompt}
<|assistant|>

```

### Eval Prompt Example 1
```text
<|user|>
Nie rozwijaj bez końca: dlaczego warto mierzyć loss? Jednym zdaniem.
<|assistant|>
```

### Eval Prompt Example 2
```text
<|user|>
Popraw tekst: Projekt może być ciekawy, ale obecnie ma zbyt wiele funkcji planowanych na start.
<|assistant|>
```

### Eval Prompt Example 3
```text
<|user|>
Czy ta diagnoza jest pewna? Wskaż ograniczenie.
<|assistant|>
```

## Label / Mask Audit

```json
{
  "assistant_only_masking": "intended, but off-by-one bug masks first response token",
  "padding_ignore_index": "yes, padding labels are -100",
  "eos_supervised": "yes, <|end|> is supervised in current examples",
  "causal_shift": "correct: x=ids[:-1], y=ids[1:]",
  "off_by_one": "bug: i <= assistant_pos should be i < assistant_pos",
  "examples_without_assistant_labels": "no, empty-label examples are skipped",
  "train_usable_examples": 1350,
  "skipped_over_context": 0,
  "skipped_no_assistant": 0,
  "skipped_empty": 0,
  "min_valid_labels_current": 6,
  "avg_valid_labels_current": 18.62148148148148
}
```

## Label Examples

```json
{
  "id": "glyph100-sft-smoke-v0-0001",
  "instruction": "Nie rozwijaj bez końca: dlaczego warto mierzyć loss? Jednym zdaniem.",
  "assistant_pos_in_x": 19,
  "x_assistant_piece": "<|assistant|>",
  "y_at_assistant_pos_piece": "▁Los",
  "current_masks_first_response_token": true,
  "should_supervise_first_response_token": true,
  "first_supervised_piece_current": "s",
  "first_supervised_piece_after_fix": "▁Los",
  "end_token_supervised_current": true,
  "valid_label_count_current": 21,
  "valid_label_count_after_fix": 22,
  "template_token_count": 42
}
```

```json
{
  "id": "glyph100-sft-smoke-v0-0002",
  "instruction": "Popraw tekst: Projekt może być ciekawy, ale obecnie ma zbyt wiele funkcji planowanych na start.",
  "assistant_pos_in_x": 23,
  "x_assistant_piece": "<|assistant|>",
  "y_at_assistant_pos_piece": "▁Projekt",
  "current_masks_first_response_token": true,
  "should_supervise_first_response_token": true,
  "first_supervised_piece_current": "▁jest",
  "first_supervised_piece_after_fix": "▁Projekt",
  "end_token_supervised_current": true,
  "valid_label_count_current": 13,
  "valid_label_count_after_fix": 14,
  "template_token_count": 38
}
```

```json
{
  "id": "glyph100-sft-smoke-v0-0003",
  "instruction": "Czy ta diagnoza jest pewna? Wskaż ograniczenie.",
  "assistant_pos_in_x": 16,
  "x_assistant_piece": "<|assistant|>",
  "y_at_assistant_pos_piece": "▁Nie",
  "current_masks_first_response_token": true,
  "should_supervise_first_response_token": true,
  "first_supervised_piece_current": ".",
  "first_supervised_piece_after_fix": "▁Nie",
  "end_token_supervised_current": true,
  "valid_label_count_current": 19,
  "valid_label_count_after_fix": 20,
  "template_token_count": 37
}
```

## ROCm NaN

```json
{
  "dtype": "fp32 default",
  "autocast": "not used",
  "grad_scaler": "not used",
  "optimizer": "fresh AdamW foreach=True fused=False",
  "lr": "5e-6 with warmup",
  "emergency_stop": {
    "phase": "sft-smoke",
    "variant": "glyph-100m",
    "dataset_name": "glyph100_sft_smoke_v0",
    "step": 3,
    "epoch": 1,
    "reason": "non_finite_loss",
    "loss": "NaN",
    "latest_checkpoint_not_overwritten": true,
    "created_at": "2026-06-24T09:20:08.787153+00:00",
    "run_config": {
      "base": "checkpoints/glyph-100m-v2_3_1-45k/step_0044000.pt",
      "resume": null,
      "train_jsonl": "data/sft/processed/glyph100_sft_smoke_v0_train.jsonl",
      "val_jsonl": "data/sft/processed/glyph100_sft_smoke_v0_val.jsonl",
      "tokenizer": "data/processed/tokenizer.model",
      "output": "checkpoints/glyph-100m-v2_3_1-44k-sft-smoke",
      "log_dir": "logs/glyph-100m-v2_3_1-44k-sft-smoke",
      "device": "cuda",
      "batch_size": 4,
      "epochs": 1,
      "max_steps": 150,
      "learning_rate": 5e-06,
      "min_lr": 1e-06,
      "weight_decay": 0.01,
      "grad_clip": 1.0,
      "warmup_steps": 10,
      "checkpoint_interval": 50,
      "eval_interval": 25,
      "val_batches": 10,
      "log_interval": 5,
      "seed": 2026,
      "tag": "glyph-100m-v2_3_1-44k-sft-smoke",
      "context_len": 512,
      "variant": "glyph-100m",
      "dataset_name": "glyph100_sft_smoke_v0",
      "dataset_report": "data/sft/glyph100_sft_smoke_v0_report.json",
      "expected_base_step": 44000,
      "expected_tokenizer_sha": "21bad2b08f1081afee40fbb6d5489d8199deebd7b81d76a34b347f2f01dd4029",
      "max_loss": 20.0
    }
  },
  "interpretation": "ROCm got NaN at step 3. Manual probes showed finite forward loss but non-finite gradients/parameters after backward/optimizer. CPU was stable. This indicates ROCm SFT backward/update instability, but label bug must be fixed first before deeper ROCm conclusions."
}
```

## CPU Smoke Length

```json
{
  "steps": 150,
  "batch_size": 4,
  "examples_seen_estimate": 600,
  "train_examples": 1350,
  "fraction_of_epoch": 0.4444444444444444,
  "avg_response_tokens": 17.558,
  "estimated_response_tokens_supervised": 10534.8,
  "interpretation": "Short enough for mechanics only; not enough to expect reliable quality, especially with first response token masked."
}
```

## Decision

- Tiny overfit CPU: not run.
- Tiny overfit ROCm safe: not run.
- Reason: critical labels/mask bug found.

## Required Next Step

1. Patch mask boundary from `i <= assistant_pos` to `i < assistant_pos`.
2. Add a label audit/unit test.
3. Re-run tiny overfit CPU only after the audit is clean.
