"""
GPT-style decoder-only transformer.
Pure PyTorch, no HuggingFace model components.
"""
import math
import os
import torch
import torch.nn as nn
import torch.nn.functional as F


class CausalSelfAttention(nn.Module):
    def __init__(self, config):
        super().__init__()
        assert config.d_model % config.n_heads == 0, "d_model must be divisible by n_heads"
        self.n_heads = config.n_heads
        self.d_head = config.d_model // config.n_heads
        self.d_model = config.d_model

        # Fused QKV projection for efficiency
        self.qkv = nn.Linear(config.d_model, 3 * config.d_model, bias=False)
        self.out_proj = nn.Linear(config.d_model, config.d_model, bias=False)
        self.attn_drop = nn.Dropout(config.dropout)
        self.resid_drop = nn.Dropout(config.dropout)

        # Causal mask: lower-triangular, registered as buffer (not a parameter)
        self.register_buffer(
            "mask",
            torch.tril(torch.ones(config.context_len, config.context_len, dtype=torch.bool))
            .view(1, 1, config.context_len, config.context_len),
        )

    def forward(self, x):
        B, T, C = x.shape

        qkv = self.qkv(x)  # (B, T, 3*C)
        q, k, v = qkv.split(self.d_model, dim=2)

        # Reshape to (B, n_heads, T, d_head)
        q = q.view(B, T, self.n_heads, self.d_head).transpose(1, 2)
        k = k.view(B, T, self.n_heads, self.d_head).transpose(1, 2)
        v = v.view(B, T, self.n_heads, self.d_head).transpose(1, 2)

        attention_impl = os.environ.get("GLYPH_ATTENTION_IMPL", "sdpa").strip().lower()
        if attention_impl == "manual":
            scores = (q @ k.transpose(-2, -1)) / math.sqrt(self.d_head)
            scores = scores.masked_fill(~self.mask[:, :, :T, :T], float("-inf"))
            probs = F.softmax(scores, dim=-1)
            probs = self.attn_drop(probs)
            y = probs @ v
        else:
            # Use PyTorch's optimized SDPA kernel. This is mathematically equivalent
            # to the manual causal attention path, but avoids extra intermediate work.
            y = F.scaled_dot_product_attention(
                q,
                k,
                v,
                attn_mask=None,
                dropout_p=self.attn_drop.p if self.training else 0.0,
                is_causal=True,
            )                                              # (B, nh, T, d_head)
        y = y.transpose(1, 2).contiguous().view(B, T, C)  # re-assemble heads
        return self.resid_drop(self.out_proj(y))


class FeedForward(nn.Module):
    def __init__(self, config):
        super().__init__()
        hidden = config.d_model * config.ffn_mult
        self.fc1 = nn.Linear(config.d_model, hidden, bias=False)
        self.fc2 = nn.Linear(hidden, config.d_model, bias=False)
        self.drop = nn.Dropout(config.dropout)

    def forward(self, x):
        return self.drop(self.fc2(F.gelu(self.fc1(x))))


class TransformerBlock(nn.Module):
    def __init__(self, config):
        super().__init__()
        self.ln1 = nn.LayerNorm(config.d_model)
        self.attn = CausalSelfAttention(config)
        self.ln2 = nn.LayerNorm(config.d_model)
        self.ffn = FeedForward(config)

    def forward(self, x):
        # Pre-LN residual connections (more stable than post-LN)
        x = x + self.attn(self.ln1(x))
        x = x + self.ffn(self.ln2(x))
        return x


class GPT(nn.Module):
    def __init__(self, config):
        super().__init__()
        self.config = config

        self.tok_emb = nn.Embedding(config.vocab_size, config.d_model)
        self.pos_emb = nn.Embedding(config.context_len, config.d_model)
        self.emb_drop = nn.Dropout(config.dropout)

        self.blocks = nn.ModuleList([TransformerBlock(config) for _ in range(config.n_layers)])
        self.ln_f = nn.LayerNorm(config.d_model)

        # LM head with weight tying to token embeddings
        self.lm_head = nn.Linear(config.d_model, config.vocab_size, bias=False)
        self.lm_head.weight = self.tok_emb.weight

        # Weight initialization
        self.apply(self._init_weights)
        # Scale down residual stream projections (GPT-2 style)
        for name, p in self.named_parameters():
            if name.endswith("out_proj.weight") or name.endswith("fc2.weight"):
                nn.init.normal_(p, mean=0.0, std=0.02 / math.sqrt(2 * config.n_layers))

        n_params_unique = sum(p.numel() for p in self.parameters())
        n_params_logical = sum(p.numel() for _, p in self.named_parameters(remove_duplicate=False))
        print(
            f"GPT initialized | layers={config.n_layers} heads={config.n_heads} "
            f"d_model={config.d_model} vocab={config.vocab_size} ctx={config.context_len}"
        )
        print(
            f"Parameters: {n_params_logical/1e6:.2f}M logical, "
            f"{n_params_unique/1e6:.2f}M unique/trainable (weight tying)"
        )

    @staticmethod
    def _init_weights(module):
        if isinstance(module, nn.Linear):
            nn.init.normal_(module.weight, mean=0.0, std=0.02)
            if module.bias is not None:
                nn.init.zeros_(module.bias)
        elif isinstance(module, nn.Embedding):
            nn.init.normal_(module.weight, mean=0.0, std=0.02)
        elif isinstance(module, nn.LayerNorm):
            nn.init.ones_(module.weight)
            nn.init.zeros_(module.bias)

    def forward(self, idx, targets=None):
        B, T = idx.shape
        assert T <= self.config.context_len, f"Sequence length {T} exceeds context_len {self.config.context_len}"
        device = idx.device

        tok = self.tok_emb(idx)                                  # (B, T, d_model)
        pos = self.pos_emb(torch.arange(T, device=device))      # (T, d_model)
        x = self.emb_drop(tok + pos)

        for block in self.blocks:
            x = block(x)

        x = self.ln_f(x)
        logits = self.lm_head(x)  # (B, T, vocab_size)

        loss = None
        if targets is not None:
            loss = F.cross_entropy(
                logits.view(-1, logits.size(-1)),
                targets.reshape(-1),
                ignore_index=-1,
            )

        return logits, loss

    @torch.no_grad()
    def generate(
        self,
        idx,
        max_new_tokens,
        temperature=1.0,
        top_k=None,
        top_p=1.0,
        repetition_penalty=1.0,
        no_repeat_ngram_size=0,
        eos_token_id=None,
    ):
        """Generate tokens, optionally stopping once every sequence emits EOS."""
        self.eval()
        finished = torch.zeros(idx.size(0), dtype=torch.bool, device=idx.device)
        for _ in range(max_new_tokens):
            # Trim to context window
            idx_cond = idx[:, -self.config.context_len:]
            logits, _ = self(idx_cond)
            logits = logits[:, -1, :]  # last token logits

            if repetition_penalty and repetition_penalty != 1.0:
                penalty = max(1.0, float(repetition_penalty))
                for batch_idx in range(idx.size(0)):
                    seen_tokens = idx[batch_idx].unique()
                    if eos_token_id is not None:
                        seen_tokens = seen_tokens[seen_tokens != int(eos_token_id)]
                    seen_logits = logits[batch_idx, seen_tokens]
                    logits[batch_idx, seen_tokens] = torch.where(
                        seen_logits < 0,
                        seen_logits * penalty,
                        seen_logits / penalty,
                    )

            if no_repeat_ngram_size and no_repeat_ngram_size > 1:
                n = int(no_repeat_ngram_size)
                for batch_idx in range(idx.size(0)):
                    sequence = idx[batch_idx].tolist()
                    if len(sequence) < n - 1:
                        continue
                    prefix = tuple(sequence[-(n - 1):])
                    banned = set()
                    for pos in range(len(sequence) - n + 1):
                        if tuple(sequence[pos:pos + n - 1]) == prefix:
                            banned.add(sequence[pos + n - 1])
                    if eos_token_id is not None:
                        banned.discard(int(eos_token_id))
                    if banned:
                        logits[batch_idx, list(banned)] = float("-inf")

            if temperature == 0.0:
                # Greedy
                idx_next = logits.argmax(dim=-1, keepdim=True)
            else:
                logits = logits / temperature
                if top_k is not None:
                    k = min(top_k, logits.size(-1))
                    top_values, _ = torch.topk(logits, k)
                    eos_keep = None
                    if eos_token_id is not None:
                        eos_keep = logits[:, int(eos_token_id)].clone()
                    logits[logits < top_values[:, [-1]]] = float("-inf")
                    if eos_keep is not None:
                        logits[:, int(eos_token_id)] = eos_keep
                if top_p is not None and top_p < 1.0:
                    sorted_logits, sorted_indices = torch.sort(logits, descending=True)
                    sorted_probs = F.softmax(sorted_logits, dim=-1)
                    cumulative_probs = torch.cumsum(sorted_probs, dim=-1)
                    sorted_remove = cumulative_probs > top_p
                    sorted_remove[:, 1:] = sorted_remove[:, :-1].clone()
                    sorted_remove[:, 0] = False
                    remove = torch.zeros_like(logits, dtype=torch.bool)
                    remove.scatter_(1, sorted_indices, sorted_remove)
                    if eos_token_id is not None:
                        remove[:, int(eos_token_id)] = False
                    logits = logits.masked_fill(remove, float("-inf"))
                probs = F.softmax(logits, dim=-1)
                idx_next = torch.multinomial(probs, num_samples=1)

            if eos_token_id is not None:
                eos = torch.full_like(idx_next, int(eos_token_id))
                idx_next = torch.where(finished.unsqueeze(1), eos, idx_next)

            idx = torch.cat((idx, idx_next), dim=1)
            if eos_token_id is not None:
                finished |= idx_next.squeeze(1).eq(int(eos_token_id))
                if bool(finished.all()):
                    break
        return idx

    def num_parameters(self, trainable_only=False):
        params = self.parameters() if not trainable_only else filter(lambda p: p.requires_grad, self.parameters())
        return sum(p.numel() for p in params)
