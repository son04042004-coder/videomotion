# Publication verification — 2026-11-03

Tested from the standalone package directory, outside the original workspace.

- Python syntax parsed for all bundled runtime/checker/demo files; Node syntax checks passed for all bundled `.mjs` files.
- Downloaded all 7 required Mixkit SFX from provider URLs; every SHA-256 matched the local reference. A second run reused the verified files.
- Rendered both k1 and k2 diagnostic projects with fresh motion graphic PNGs, cursor clicks, camera movement, a two-scene transition, subtitles and sound effects.
- FFprobe for both outputs: 1080 × 1920, 30/1 fps, 5.53 seconds, video + audio. Loudness QA: -14.2 LUFS, -6.5 dBFS peak.
- Generated thumbnails and contact sheets for both channels; visually checked the k1 contact sheet and k2 thumbnail.
- Content checker: 8 input files, 0 errors, 0 review findings.
- Vibi payload mock: emotion tags remain in text; speed 1.1, stability 0, style 0.6 are passed intact. No live paid TTS request was made.
- Compared bundled files against non-empty API credential values from the local environment without printing the values; no matches found.

The diagnostic audio is a sine tone, not synthesized speech. This verifies rendering and packaging; actual voice generation/alignment still requires the user's Vibi key, API access, Faster Whisper and its downloaded model. Live logged-in browser capture, publishing to TikTok and Drive upload were not exercised. Windows is the verified operating system.
