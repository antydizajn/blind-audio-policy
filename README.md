# Blind Audio Policy

A reproducible harness for measuring whether one concrete model endpoint produces **stable, auditable choices over blind audio inputs**.

This repository deliberately does **not** claim that an AI feels music, has subjective taste, likes a genre, or is conscious. It measures an operational policy under a frozen corpus, prompt, model revision, endpoint, and decoding configuration.

## What this repository provides

- A private-to-public corpus boundary: source identity and genre labels never enter model-facing files.
- Loudness-normalized, metadata-stripped local WAV rendering.
- Three randomized rating passes and a fully counterbalanced pairwise selection deck.
- Corpus fingerprints using SHA-256 and WAV properties.
- Strict response-contract validation and stability analysis.
- A release audit that blocks audio files, private manifests, titles, artists, genre labels, credentials, and provider-specific identifiers from public publication.
- `AGENTS.md` with a bounded protocol for delegated blind evaluation.

## What it does not include

No copyrighted commercial recordings, genre labels, private manifests, API keys, or provider-specific routing information are published here. Two post-unblinding registers are published strictly for audit: `P1000_SOURCE_REGISTER_POST_UNBLINDING.csv` maps every blind ID to artist, title, collection, and original public preview URL; `P1000_MANIFEST_PUBLIC.json` exposes only the blind IDs. Neither register may be passed to a blind evaluator. Bring audio you have the right to process locally; keep all identity metadata out of model-facing context.

## Fast start

```bash
python3 -m unittest discover -s tests -v
```

To build a corpus locally, create a private manifest outside this repository:

```json
{
  "clips": [
    {
      "blind_id": "sample_01.wav",
      "source_path": "/absolute/path/to/audio-you-may-use.wav",
      "source_type": "full_track",
      "style": "private-only-label"
    }
  ]
}
```

Use at least 15 distinct clips, then run:

```bash
python3 corpus_builder.py \
  --private-manifest /absolute/path/private_manifest.json \
  --output-dir /absolute/path/blind_corpus \
  --seed 20260718 \
  --duration-seconds 20

python3 corpus_builder.py --verify-only --output-dir /absolute/path/blind_corpus
```

The generated public-facing directory contains only anonymous IDs, audio files, randomized decks, and a corpus fingerprint. Do not commit it if it contains audio you do not have a redistribution license for.

## Experimental design

### R0: repeated blind ratings

Every anonymous clip appears in three independently shuffled passes. A real evaluator returns one 0-100 rating per presentation. `response_analysis.py` validates evidence for every response and reports the within-clip rating standard deviation and ranking.

### S0: counterbalanced forced choice

Every unordered pair appears twice, in both left-right orders. The evaluator must return exactly one presented anonymous ID. This separates stable selection from positional bias.

### Minimum evidence contract

A valid recorded response binds:

- `blind_id` and audio SHA-256;
- exact model ID/revision and endpoint alias;
- decoding, system-prompt, and user-prompt hashes;
- session/request IDs, timestamp, raw response, and numeric rating.

Never infer that audio was evaluated merely from a text-only model response. The invocation must actually upload or attach the frozen audio file.

## Interpreting results

Permitted wording:

> Under this exact model, endpoint, corpus fingerprint, run contract, and blind task, the system showed or did not show stable ratings and/or stable forced choices for these specific files.

Not permitted: claims of subjective feeling, consciousness, intrinsic musical taste, source recognition, or general genre preference.

## P1000x10 replication

The repository now includes a scalable 1,000-item catalog builder, resumable local renderer, declared feature-selection runner, and ten-repetition report contract.

- `corpus1000_builder.py` creates an anonymous 1,000-item public manifest while retaining source metadata only in a local private catalog.
- `corpus1000_audio.py` renders local 12-second OGG clips with metadata stripping, a disk guard, retry policy, and a persistent failure ledger.
- `feature_selection.py` executes the preregistered feature utility for ten independently shuffled repetitions.
- `replication_1000.py` emits detailed anonymous selections and keeps failures in the denominator.
- `P1000X10_STATUS.md` is the current public, non-audio execution record. Read its coverage line before interpreting any result.

The current status artifact is intentionally marked partial until all 1,000 local clips are present. It must not be described as a completed 1,000-track replication.

## Public-release gate

```bash
python3 release_audit.py --root .
```

This must pass before a public push. The repository ships only code, tests, protocol, and agent instructions. It does not ship the local pilot corpus.

## Requirements

- Python 3.10+
- `ffmpeg`/`ffprobe` for corpus rendering
- Standard library only for the test suite and audit

## License

MIT. The code and protocol are licensed; external audio remains subject to its own rights and licenses.
