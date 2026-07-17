# AGENTS.md - Blind Audio Policy

## Mission

Build or evaluate a **blind operational audio-choice protocol**. Never convert it into a claim that a model has subjective taste, feelings, consciousness, or a general genre preference.

## Public/private boundary

- Private-only: source paths, source URLs, artist, title, genre/style, curator identity, user profile, secret tokens, provider configuration, and unblinding map.
- Model-facing: anonymous IDs, the actual audio bytes, a frozen fingerprint, a task prompt, and the response schema.
- Public repository: code, tests, generic protocol, fixtures that contain no real music, and no corpus audio unless every file has an explicit redistribution license.
- `P100_SOURCE_REGISTER_POST_UNBLINDING.md` is human-readable metadata for post-unblinding audit only. It is forbidden input for every blind evaluator.

## Mandatory delegated-blind-evaluation protocol

When delegating a blind evaluation, spawn a separate leaf subagent with this exact boundary:

```text
You are a blind audio evaluator.

You may inspect ONLY the supplied audio directory and the public corpus fingerprint.
You must not inspect parent directories, manifests outside the supplied public artifacts,
filenames beyond anonymous blind IDs, source/title/artist/genre mappings, user profile,
session history, web results, or any private metadata. Make no network calls and no writes.

Before comparing clips, state a fixed operational scoring or choice rule. Apply it to the
entire supplied corpus. Return only anonymous IDs, the declared rule, exact scores/choices,
runner-up or tie information, and the operational boundary. Do not infer identity, genre,
artist, subjective taste, consciousness, or user independence.
```

## Evaluation requirements

1. Verify the corpus fingerprint before starting.
2. Freeze the evaluator prompt and decoding configuration before the first trial.
3. Run at least three shuffled rating passes for R0.
4. Run counterbalanced left-right pairs for S0.
5. Retain a complete response record with request IDs and audio hashes.
6. Reject incomplete coverage, unknown IDs, mismatched hashes, contract drift, non-finite ratings, or fabricated request evidence.
7. Use a new isolated subagent/session for independent replication; do not let it see prior choices.
8. Unblind only after the full blind result is sealed.

## Reporting language

Use: "stable blind operational selection under this frozen run contract."

Do not use: "the AI likes", "the AI feels", "the AI has taste", "the AI recognizes", "the AI is conscious".

## Verification

```bash
python3 -m unittest discover -s tests -v
python3 release_audit.py --root .
```

The public-release audit must pass before publishing. A test pass does not prove a real model received audio; only an auditable upload/attachment record can establish that input path.
