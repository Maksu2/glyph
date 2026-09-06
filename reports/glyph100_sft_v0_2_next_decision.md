# Glyph-100M SFT v0.2 next decision

## Verdict

- verdict: `B`
- label: `v0.2 poprawia częściowo`
- recommendation: Kolejny krok to projekt datasetu v0.3 albo ostrożny plan SFT v1; nie uruchamiać automatycznie.

## Constraints

- Do not run SFT v1 automatically.
- Do not run further pretraining.
- Do not use 50k as SFT base.
- Do not publish as final chatbot.

## Evidence

- eval rows: `100`
- modes: `['greedy', 'repetition_guard']`
- pairwise totals: `{'sft_v0_2_vs_sft_v0_1': {'sft_v0_2': 36, 'tie': 145, 'sft_v0_1': 19}, 'sft_v0_2_vs_base44k': {'sft_v0_2': 111, 'tie': 83, 'base44k': 6}, 'sft_v0_1_vs_base44k': {'sft_v0_1': 101, 'tie': 95, 'base44k': 4}}`

- base44k: avg `-0.16`, repetition `73`, first-token `0`, web `6`, pseudo `0`
- sft_v0_1: avg `2.94`, repetition `29`, first-token `40`, web `4`, pseudo `0`
- sft_v0_2: avg `3.40`, repetition `12`, first-token `49`, web `13`, pseudo `0`
