# Glyph-100M v2.4.2 P100 continuation to 10k

**Status: PASS**

- run_id: `glyph100-v242-p100-5k-to-10k-001`
- started_at_utc: `2026-08-08T15:37:09.378373+00:00`
- finished_at_utc: `2026-08-08T17:59:37.686002+00:00`
- wall_seconds: `8756.069478886`
- gpu: `{'name': 'Tesla P100-PCIE-16GB', 'compute_capability': '6.0', 'total_vram_bytes': 17059545088, 'free_vram_bytes': 16723869696, 'pytorch': '2.10.0+cu126', 'cuda': '12.6', 'cudnn': 91002}`
- smoke: `{'status': 'PASS', 'run_id': 'glyph100-v242-p100-5k-to-10k-001', 'start_step': 5000, 'end_step': 5100, 'duration_seconds': 186.93943890599996, 'average_tokens_per_second': 9483.8, 'validation': [{'step': 5050, 'val_loss': 4.6221}, {'step': 5100, 'val_loss': 4.6002}], 'checkpoint': {'step': 5100, 'current_step': 5100, 'variant': 'glyph-100m', 'dataset_name': 'glyph100_dataset_v2_4_2_core', 'tokenizer_sha256': '21bad2b08f1081afee40fbb6d5489d8199deebd7b81d76a34b347f2f01dd4029', 'batch_size': 4, 'gradient_accumulation_steps': 8, 'effective_tokens_per_step': 16384, 'context_length': 512, 'path': '/kaggle/working/glyph100-v242-p100-5k-to-10k-001/smoke/checkpoints/step_0005100.pt', 'size': 1175129201, 'sha256': '31e51e9b38e5bb381f808609206d2b94170f58f8b36cbc9a06a28a73e473f9bf', 'model_tensors': 113, 'optimizer_state_present': True, 'scheduler_state_present': True, 'sampler_state_present': True}, 'bad_terms': [], 'training_continuation_allowed': True}`
- continuation_start_step: `5100`
- continuation_end_step: `10000`
- continuation_duration_seconds: `8346.548747243`
- continuation_average_tokens_per_second: `9643.695918367346`
- validation: `[{'step': 5500, 'val_loss': 4.4764}, {'step': 6000, 'val_loss': 4.3395}, {'step': 6500, 'val_loss': 4.2492}, {'step': 7000, 'val_loss': 4.1749}, {'step': 7500, 'val_loss': 4.1136}, {'step': 8000, 'val_loss': 4.0573}, {'step': 8500, 'val_loss': 4.0127}, {'step': 9000, 'val_loss': 3.9748}, {'step': 9500, 'val_loss': 3.946}, {'step': 10000, 'val_loss': 3.9023}]`
- final_checkpoint: `{'step': 10000, 'current_step': 10000, 'variant': 'glyph-100m', 'dataset_name': 'glyph100_dataset_v2_4_2_core', 'tokenizer_sha256': '21bad2b08f1081afee40fbb6d5489d8199deebd7b81d76a34b347f2f01dd4029', 'batch_size': 4, 'gradient_accumulation_steps': 8, 'effective_tokens_per_step': 16384, 'context_length': 512, 'path': '/kaggle/working/glyph100-v242-p100-5k-to-10k-001/continuation/checkpoints/step_0010000.pt', 'size': 1175129265, 'sha256': 'e32d34baff7c522a77a83c5ec1812dd83798c31c8b4cdefe93c729a4441ab4ce', 'model_tensors': 113, 'optimizer_state_present': True, 'scheduler_state_present': True, 'sampler_state_present': True}`
- latest_checkpoint: `{'step': 10000, 'current_step': 10000, 'variant': 'glyph-100m', 'dataset_name': 'glyph100_dataset_v2_4_2_core', 'tokenizer_sha256': '21bad2b08f1081afee40fbb6d5489d8199deebd7b81d76a34b347f2f01dd4029', 'batch_size': 4, 'gradient_accumulation_steps': 8, 'effective_tokens_per_step': 16384, 'context_length': 512, 'path': '/kaggle/working/glyph100-v242-p100-5k-to-10k-001/continuation/checkpoints/latest.pt', 'size': 1175128847, 'sha256': '4c32078f527b9ce13df5053251aeee3b622db4c6a5640e33b32e06c32d3d9331', 'model_tensors': 113, 'optimizer_state_present': True, 'scheduler_state_present': True, 'sampler_state_present': True}`
- input_5k_checkpoint_unchanged: `True`
- next_training_started: `False`
