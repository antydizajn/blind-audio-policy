# P1000x10 local feature-selection replication status

## Scope

This is a preregistered declared feature-utility run over the locally rendered subset of an intended 1,000-track blind corpus. It is **not** a subjective-taste or consciousness claim, and it is not evidence that a remote model endpoint received audio.

## Executed run

| field | value |
|---|---:|
| Intended catalog | 1,000 unique artist-track pairs |
| Local OGG files rendered at run time | 697 |
| Repetitions | 10 |
| Scheduled trials | 6970 |
| Scored trials | 6970 |
| Feature extraction failures | 0 |

## Frozen declared utility

```text
U=0.25*T+0.20*D+0.20*C+0.20*F+0.15*N-(0.07*Qclip+0.06*Qsilence+0.10*Qrepeat)
```

Positive components are corpus-relative percentiles. Penalties are normalized within the locally present corpus. The first repetition's top ten anonymous IDs were:

```text
p0686.ogg, p0699.ogg, p0611.ogg, p0643.ogg, p0635.ogg, p0677.ogg, p0653.ogg, p0672.ogg, p0673.ogg, p0676.ogg
```

## Important limitation

The full 1,000-file render has not completed because external preview transport produced timeouts and partial streams. The downloader records failures rather than silently deleting them; therefore this report is deliberately labeled partial. The public repository contains no external audio bytes or identity map.
