from dataclasses import asdict, dataclass, field


PROJECT_NAME = "Glyph"
MODEL_NAME = "Glyph-27M"
MODEL_VARIANT = "Base"
MODEL_FULL_NAME = f"{MODEL_NAME} {MODEL_VARIANT}"
MODEL_DESCRIPTION = (
    "Glyph-27M is a small Polish decoder-only Transformer trained from scratch on a homelab."
)


@dataclass
class ModelConfig:
    vocab_size: int = 16000
    context_len: int = 256
    d_model: int = 512
    n_heads: int = 8
    n_layers: int = 6
    ffn_mult: int = 4
    dropout: float = 0.1


MODEL_VARIANTS = {
    "glyph-27m": {
        "display_name": "Glyph-27M",
        "vocab_size": 16000,
        "context_len": 256,
        "d_model": 512,
        "n_heads": 8,
        "n_layers": 6,
        "ffn_mult": 4,
        "dropout": 0.1,
    },
    "glyph-100m": {
        "display_name": "Glyph-100M",
        "vocab_size": 16000,
        "context_len": 512,
        "d_model": 768,
        "n_heads": 12,
        "n_layers": 12,
        "ffn_mult": 4,
        "dropout": 0.1,
    },
}


def normalize_variant_name(name: str | None) -> str:
    value = (name or "glyph-27m").strip().lower()
    aliases = {
        "27m": "glyph-27m",
        "glyph27m": "glyph-27m",
        "glyph-27m-base": "glyph-27m",
        "100m": "glyph-100m",
        "glyph100m": "glyph-100m",
    }
    value = aliases.get(value, value)
    if value not in MODEL_VARIANTS:
        valid = ", ".join(sorted(MODEL_VARIANTS))
        raise ValueError(f"Unknown model variant {name!r}; valid variants: {valid}")
    return value


def get_model_config(variant: str | None = None, **overrides) -> ModelConfig:
    """Return a ModelConfig for a named Glyph variant without mutating defaults."""
    key = normalize_variant_name(variant)
    values = {
        name: value
        for name, value in MODEL_VARIANTS[key].items()
        if name in ModelConfig.__dataclass_fields__
    }
    values.update({name: value for name, value in overrides.items() if value is not None})
    return ModelConfig(**values)


def model_variant_metadata(variant: str | None = None) -> dict:
    key = normalize_variant_name(variant)
    cfg = get_model_config(key)
    metadata = dict(MODEL_VARIANTS[key])
    metadata["variant"] = key
    metadata["model_config"] = asdict(cfg)
    metadata["ffn_dim"] = cfg.d_model * cfg.ffn_mult
    metadata["norm"] = "pre-layernorm"
    metadata["activation"] = "GELU"
    metadata["weight_tying"] = True
    return metadata


@dataclass
class TrainConfig:
    # Paths
    data_path: str = "data/processed/tokens.bin"
    val_data_path: str = "data/processed/val_tokens.bin"
    checkpoint_dir: str = "checkpoints"
    log_dir: str = "logs/glyph-27m"
    tokenizer_path: str = "data/processed/tokenizer.model"
    dataset_metadata_path: str = ""
    dataset_name: str = "glyph27m_legacy_pretraining"

    # Optimization
    batch_size: int = 32
    max_lr: float = 3e-4
    min_lr: float = 3e-5
    weight_decay: float = 0.1
    beta1: float = 0.9
    beta2: float = 0.95
    grad_clip: float = 1.0
    gradient_accumulation_steps: int = 1
    train_sampling: str = "random"
    data_seed: int = 2026
    eval_seed: int = 2027

    # Schedule
    max_steps: int = 200_000
    warmup_steps: int = 2_000

    # Logging / checkpointing
    log_interval: int = 10
    eval_interval: int = 500
    eval_batches: int = 10
    checkpoint_interval: int = 1_000


def get_train_config(variant: str | None = None) -> TrainConfig:
    key = normalize_variant_name(variant)
    cfg = TrainConfig()
    if key == "glyph-100m":
        cfg.data_path = "data/processed/glyph100_train.bin"
        cfg.val_data_path = "data/processed/glyph100_val.bin"
        cfg.checkpoint_dir = "checkpoints/glyph-100m"
        cfg.log_dir = "logs/glyph-100m"
        cfg.tokenizer_path = "data/processed/tokenizer.model"
        cfg.dataset_metadata_path = "data/processed/glyph100_metadata.json"
        cfg.dataset_name = "glyph100_stage1_candidate"
        cfg.batch_size = 4
        cfg.max_lr = 2e-4
        cfg.min_lr = 2e-5
        cfg.weight_decay = 0.1
        cfg.grad_clip = 1.0
        cfg.gradient_accumulation_steps = 8
        cfg.train_sampling = "shuffled_blocks"
        cfg.data_seed = 2026
        cfg.eval_seed = 2027
        cfg.max_steps = 200_000
        cfg.warmup_steps = 2_000
        cfg.log_interval = 10
        cfg.eval_interval = 250
        cfg.eval_batches = 64
        cfg.checkpoint_interval = 500
    return cfg


@dataclass
class FinetuneConfig:
    base_model: str = "checkpoints/final.pt"
    output_dir: str = "checkpoints/sft-v0"
    train_jsonl: str = "data/sft/processed/sft_v0_train.jsonl"
    val_jsonl: str = "data/sft/processed/sft_v0_val.jsonl"
    dataset_names: list = field(default_factory=lambda: [
        "tatiana-merz/alpaca_pl",
        "Bielik-AI/alpaca_data_pl",
        "clarin-pl/alpaca_pl",
    ])

    batch_size: int = 16
    max_lr: float = 2e-5
    min_lr: float = 2e-6
    weight_decay: float = 0.01
    grad_clip: float = 1.0
    max_steps: int = 1_000
    epochs: int = 1
    warmup_steps: int = 10
    checkpoint_interval: int = 50
    eval_interval: int = 25
    eval_batches: int = 10
    log_interval: int = 5

    # Special tokens
    user_token: str = "<|user|>"
    assistant_token: str = "<|assistant|>"
    end_token: str = "<|end|>"
