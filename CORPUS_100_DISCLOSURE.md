# The local P100 corpus is intentionally not published

This project has an exact 100-file anonymous local corpus. Its public counterpart contains only anonymous IDs and SHA-256 fingerprints; it intentionally contains neither audio bytes nor the private title/artist/genre map.

## Why the files are absent

1. The local files are derived from third-party commercial music previews. The repository does not have redistribution rights for them.
2. Publishing the private identity map makes the corpus non-blind, defeating the experiment.

## What is public instead

- `data/preview100/manifest_public.json`: 100 anonymous IDs plus immutable SHA-256 fingerprints.
- `preview100_integrity.py`: verifies an authorized local copy matches exactly.
- `AGENTS.md`: a protocol for sending *only* local anonymous audio plus this manifest to an isolated subagent.

The exact audio and identity map remain local/private. An evaluator who lawfully holds the same local corpus can verify the exact 100-file corpus before a blind run without accessing the identity map.
