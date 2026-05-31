# firestorm-cameras

National-reach wildfire **camera catalog** for [FIRESTORM](https://github.com/Deasus/Firestorm),
snapshotted from the **AlertWest** public API so the single-file frontend can read it CORS-cleanly.

## Why a bridge (not a direct browser fetch)

AlertWest's API (`alertwest.live/api/firecams/v0/cameras`) returns
`access-control-allow-origin: *` on the CORS **preflight** but **not** on the actual GET response,
so a browser blocks the cross-origin read (verified 2026-05-31: real Chromium →
*"No 'Access-Control-Allow-Origin' header is present"*). A server-side cron has no CORS, fetches
fine, and republishes to `raw.githubusercontent.com` (which **is** CORS-open). Bonus: avoids a
1.2 MB per-viewer download and decouples FIRESTORM from AlertWest uptime.

## What it gives FIRESTORM

~1,700 live PTZ wildfire cameras across **13 western states + Hawaii** (CA, HI, NV, OR, MT, ID, WA,
CO, WY, NM, AZ, UT + Alberta) — ground-truth eyes to confirm a satellite/thermal detection.

## Imagery licensing — important

ALERT* camera imagery is **CC BY-NC-ND 4.0** (non-commercial, no-derivatives). This pipeline stores
only camera **metadata + the live-frame URL** — it does **not** cache or re-host images. The FIRESTORM
frontend **hot-links** the live frame (display-only, no alteration) with attribution. **Confirm written
redistribution terms with AlertWest / ALERTCalifornia before wide rollout.**

## Output — `data/cameras.json`

```jsonc
{ "generated_at": "...", "count": 1783, "source": "AlertWest / ALERTCalifornia ...",
  "cameras": [ {"name","lat","lng","state","county","img","src"} ] }
```
Frontend reads `raw.githubusercontent.com/Deasus/firestorm-cameras/main/data/cameras.json`.

## Run locally
```bash
python fetch_cameras.py     # stdlib only
```
Hourly GHA cron (`.github/workflows/update-cameras.yml`); camera locations are near-static so no
aggressive cadence needed.
