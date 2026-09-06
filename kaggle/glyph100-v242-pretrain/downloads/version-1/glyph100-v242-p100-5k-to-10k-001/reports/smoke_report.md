# Glyph-100M v2.4.2 100-step P100 smoke

**Status: PASS**

- run_id: `glyph100-v242-p100-5k-to-10k-001`
- start_step: `5000`
- end_step: `5100`
- duration_seconds: `186.93943890599996`
- average_tokens_per_second: `9483.8`
- validation: `[{'step': 5050, 'val_loss': 4.6221}, {'step': 5100, 'val_loss': 4.6002}]`
- checkpoint: `{'step': 5100, 'current_step': 5100, 'variant': 'glyph-100m', 'dataset_name': 'glyph100_dataset_v2_4_2_core', 'tokenizer_sha256': '21bad2b08f1081afee40fbb6d5489d8199deebd7b81d76a34b347f2f01dd4029', 'batch_size': 4, 'gradient_accumulation_steps': 8, 'effective_tokens_per_step': 16384, 'context_length': 512, 'path': '/kaggle/working/glyph100-v242-p100-5k-to-10k-001/smoke/checkpoints/step_0005100.pt', 'size': 1175129201, 'sha256': '31e51e9b38e5bb381f808609206d2b94170f58f8b36cbc9a06a28a73e473f9bf', 'model_tensors': 113, 'optimizer_state_present': True, 'scheduler_state_present': True, 'sampler_state_present': True}`
- bad_terms: `[]`
- training_continuation_allowed: `True`
