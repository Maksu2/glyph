# Bluetooth acoustic latency test

This is **measured end-to-end acoustic latency including microphone/capture path**.
It is not presented as pure Bluetooth latency.

## Statistics

- Valid: 24 / 24
- Minimum: 213.656 ms
- Median: 243.221 ms
- Mean: 243.224 ms
- p95: 262.293 ms
- Maximum: 300.752 ms
- Standard deviation: 17.876 ms
- Peak-to-peak jitter: 87.097 ms

## Capture timing

- Mapping: 5th percentile of chunk read-end minus nominal frame time
- Capture anchor p05–p95 spread: 0.328 ms
- PulseAudio reported latencies are listed in `results.json`.

## Per-trial results

| Trial | Latency ms | Correlation | SNR dB | Peak dBFS | Valid |
|---:|---:|---:|---:|---:|:---:|
| 1 | 300.752 | 0.802 | 18.7 | -43.5 | yes |
| 2 | 246.109 | 0.824 | 24.7 | -43.0 | yes |
| 3 | 238.482 | 0.804 | 25.6 | -43.3 | yes |
| 4 | 215.588 | 0.823 | 21.2 | -43.4 | yes |
| 5 | 232.565 | 0.810 | 24.4 | -43.5 | yes |
| 6 | 256.494 | 0.804 | 25.9 | -43.2 | yes |
| 7 | 251.829 | 0.774 | 23.5 | -43.5 | yes |
| 8 | 254.365 | 0.829 | 24.0 | -43.2 | yes |
| 9 | 231.442 | 0.815 | 22.6 | -43.4 | yes |
| 10 | 241.239 | 0.821 | 19.5 | -43.4 | yes |
| 11 | 221.796 | 0.822 | 21.6 | -43.3 | yes |
| 12 | 245.505 | 0.818 | 22.4 | -43.5 | yes |
| 13 | 234.787 | 0.825 | 19.0 | -43.3 | yes |
| 14 | 263.316 | 0.806 | 17.7 | -43.4 | yes |
| 15 | 239.682 | 0.780 | 23.8 | -43.6 | yes |
| 16 | 256.252 | 0.818 | 21.1 | -43.5 | yes |
| 17 | 246.896 | 0.807 | 18.0 | -43.4 | yes |
| 18 | 232.683 | 0.824 | 25.3 | -43.5 | yes |
| 19 | 252.043 | 0.814 | 23.0 | -43.2 | yes |
| 20 | 229.703 | 0.828 | 24.6 | -43.1 | yes |
| 21 | 254.214 | 0.805 | 14.3 | -43.2 | yes |
| 22 | 245.204 | 0.811 | 21.7 | -43.5 | yes |
| 23 | 213.656 | 0.797 | 20.2 | -43.3 | yes |
| 24 | 232.779 | 0.790 | 21.3 | -43.5 | yes |

## Definition

Start: `time.monotonic_ns()` immediately before spawning one `paplay` process.

End: matched acoustic marker in the 48 kHz microphone waveform, mapped to the
monotonic clock from continuous small `parecord` reads.

Included: process startup, PulseAudio output, BlueZ/A2DP, Bluetooth radio,
speaker buffering/DSP, acoustic propagation, microphone, ADC, ALSA/PulseAudio
capture buffering, and delivery to the recording client.
