# NARIS W04 presentation audio source

Place production SFX masters here using the exact asset ID as the filename:

`<ASSET_ID>.wav`

Example:

`NARIS-W04-AUD-PARRY-0001.wav`

## Import contract

- WAV container
- PCM / uncompressed
- 48,000 Hz
- 24-bit source master
- 1 or 2 channels; mono is preferred for spatial one-shots
- no clipping; source-plan target ceiling is -1 dBFS
- retain a natural decay tail; remove accidental leading silence
- filename must match the registered NARIS asset ID exactly

The Unreal intake script validates the WAV header before import. Missing files are
reported as skipped and remain unbound. It never fabricates a SoundWave.
