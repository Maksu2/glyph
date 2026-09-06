#!/usr/bin/env python3
"""
Text generation from a trained checkpoint.

Usage:
  python generate.py "Stolica Polski to"
  python generate.py "Był sobie raz" --max-tokens 200 --temperature 0.8 --top-k 40 --no-repeat-ngram-size 4
  python generate.py "Opis" --checkpoint checkpoints/step_0050000.pt
"""
import sys
import argparse
import os
import torch
from pathlib import Path
from contextlib import redirect_stdout

sys.path.insert(0, str(Path(__file__).parent))
from config import ModelConfig
from model import GPT


def configure_cpu_threads():
    raw = (
        os.environ.get("GLYPH_INFER_THREADS")
        or os.environ.get("MINIGPT_INFER_THREADS")
        or os.environ.get("OMP_NUM_THREADS")
    )
    if not raw:
        return
    try:
        threads = max(1, int(raw))
    except ValueError:
        return
    torch.set_num_threads(threads)
    try:
        torch.set_num_interop_threads(threads)
    except RuntimeError:
        pass


def load_model(checkpoint_path: str) -> tuple[GPT, object]:
    """Load model and tokenizer from checkpoint."""
    ckpt = torch.load(checkpoint_path, map_location="cpu", weights_only=False)

    # Reconstruct model config from checkpoint if available
    cfg_dict = ckpt.get("model_config", {})
    cfg = ModelConfig(**{k: v for k, v in cfg_dict.items() if hasattr(ModelConfig, k) or k in ModelConfig.__dataclass_fields__})

    model = GPT(cfg)
    model.load_state_dict(ckpt["model"])
    model.eval()
    return model, cfg


def load_tokenizer(tokenizer_path: str):
    try:
        import sentencepiece as spm
    except ImportError:
        print("sentencepiece not installed: pip install sentencepiece", file=sys.stderr)
        sys.exit(1)

    sp = spm.SentencePieceProcessor()
    sp.load(tokenizer_path)
    return sp


def find_latest_checkpoint(ckpt_dir: str) -> str | None:
    latest = Path(ckpt_dir) / "latest.pt"
    if latest.exists():
        return str(latest)
    import glob
    ckpts = sorted(glob.glob(str(Path(ckpt_dir) / "step_*.pt")))
    return ckpts[-1] if ckpts else None


def main():
    parser = argparse.ArgumentParser(description="Generate text from Glyph-27M")
    parser.add_argument("prompt", type=str, help="Text prompt to continue")
    parser.add_argument("--checkpoint", type=str, default=None,
                        help="Path to checkpoint (default: latest)")
    parser.add_argument("--tokenizer", type=str, default="data/processed/tokenizer.model",
                        help="Path to SentencePiece model")
    parser.add_argument("--max-tokens", type=int, default=150,
                        help="Number of new tokens to generate (default: 150)")
    parser.add_argument("--temperature", type=float, default=0.8,
                        help="Sampling temperature (0=greedy, default: 0.8)")
    parser.add_argument("--top-k", type=int, default=40,
                        help="Top-k sampling (default: 40, 0=disabled)")
    parser.add_argument("--top-p", type=float, default=1.0,
                        help="Nucleus/top-p sampling (default: 1.0=disabled)")
    parser.add_argument("--repetition-penalty", type=float, default=1.0,
                        help="Penalty for tokens already seen in the context (default: 1.0=disabled)")
    parser.add_argument("--no-repeat-ngram-size", type=int, default=0,
                        help="Block repeated token n-grams of this size (default: 0=disabled)")
    args = parser.parse_args()
    configure_cpu_threads()

    # Find checkpoint
    ckpt_path = args.checkpoint or find_latest_checkpoint("checkpoints")
    if not ckpt_path or not Path(ckpt_path).exists():
        print("No checkpoint found. Train a model first: python train.py", file=sys.stderr)
        sys.exit(1)

    # Find tokenizer
    if not Path(args.tokenizer).exists():
        print(f"Tokenizer not found: {args.tokenizer}", file=sys.stderr)
        print("Run preprocessing first: python data/preprocess.py", file=sys.stderr)
        sys.exit(1)

    print(f"Loading checkpoint: {ckpt_path}", file=sys.stderr)
    with redirect_stdout(sys.stderr):
        model, cfg = load_model(ckpt_path)
    sp = load_tokenizer(args.tokenizer)

    # Encode prompt
    prompt_ids = sp.encode(args.prompt, out_type=int)
    if not prompt_ids:
        print("Empty prompt after tokenization", file=sys.stderr)
        sys.exit(1)

    # Truncate prompt to context_len - max_tokens (leave room for generation)
    max_prompt_len = cfg.context_len - 1
    if len(prompt_ids) > max_prompt_len:
        print(f"Prompt truncated to {max_prompt_len} tokens", file=sys.stderr)
        prompt_ids = prompt_ids[-max_prompt_len:]

    idx = torch.tensor([prompt_ids], dtype=torch.long)

    top_k = args.top_k if args.top_k > 0 else None

    print(
        f"--- Generating ({args.max_tokens} tokens, temp={args.temperature}, "
        f"top_k={top_k}, top_p={args.top_p}, repetition_penalty={args.repetition_penalty}, "
        f"no_repeat_ngram_size={args.no_repeat_ngram_size}) ---",
        file=sys.stderr,
    )
    print()

    with torch.no_grad():
        output_ids = model.generate(
            idx,
            max_new_tokens=args.max_tokens,
            temperature=args.temperature,
            top_k=top_k,
            top_p=args.top_p,
            repetition_penalty=args.repetition_penalty,
            no_repeat_ngram_size=args.no_repeat_ngram_size,
            eos_token_id=sp.eos_id(),
        )

    all_ids = output_ids[0].tolist()
    generated_ids = all_ids[len(prompt_ids) :]
    ended_by_eos = bool(generated_ids and generated_ids[-1] == sp.eos_id())
    text_ids = generated_ids[:-1] if ended_by_eos else generated_ids
    text = sp.decode(prompt_ids + text_ids)
    print(
        f"Generated {len(generated_ids)} model tokens (ended_by_eos={ended_by_eos})",
        file=sys.stderr,
    )
    print(text)


if __name__ == "__main__":
    main()
