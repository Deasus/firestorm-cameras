#!/usr/bin/env python3
"""
FIRESTORM wildfire-camera pipeline — snapshots the AlertWest public camera
catalog (alertwest.live) to a slim GeoJSON-ish JSON the FIRESTORM frontend
reads via raw.githubusercontent.com.

WHY A BRIDGE (not a direct browser fetch):
The AlertWest API returns `access-control-allow-origin: *` on the CORS PREFLIGHT
(OPTIONS) but does NOT send it on the actual GET response, so a browser blocks
the cross-origin read (verified 2026-05-31: real Chromium gets
"No 'Access-Control-Allow-Origin' header is present on the requested resource").
A server-side cron has no CORS — it fetches fine — and re-publishes to
raw.githubusercontent.com, which IS CORS-open. This also avoids a 1.2 MB
per-viewer download and decouples FIRESTORM from AlertWest uptime.

WHAT THIS GIVES FIRESTORM: ~1,700 live PTZ wildfire cameras across 13 western
states + Hawaii (CA, HI, NV, OR, MT, ID, WA, CO, WY, NM, AZ, UT + Alberta) —
ground-truth eyes to CONFIRM a satellite/thermal detection (column, color,
spread direction, real-vs-false). National reach no other free source matches.

IMAGERY LICENSING — IMPORTANT: ALERT* camera imagery is CC BY-NC-ND 4.0
(non-commercial, no-derivatives). This pipeline stores only camera METADATA +
the live-frame URL — it does NOT cache/re-host the images. The frontend
HOT-LINKS the live frame (display-only, no alteration) with attribution. Confirm
written redistribution terms with AlertWest/ALERTCalifornia before wide rollout.

OUTPUT: data/cameras.json
Shape: { "generated_at": ISO8601, "count": N, "source": "AlertWest",
         "cameras": [ {name, lat, lng, state, county, img, src}, ... ] }

SOURCE: https://alertwest.live/api/firecams/v0/cameras  (public, no auth)
Requires: only the Python stdlib (urllib) — no third-party deps.
"""
from __future__ import annotations
import json
import os
import sys
import urllib.request
from datetime import datetime, timezone

FEED = "https://alertwest.live/api/firecams/v0/cameras"
OUT_PATH = os.path.join(os.path.dirname(__file__), "data", "cameras.json")


def main() -> int:
    req = urllib.request.Request(FEED, headers={"User-Agent": "firestorm-cameras/1.0 (+github.com/Deasus)"})
    with urllib.request.urlopen(req, timeout=30) as r:
        raw = json.loads(r.read().decode("utf-8"))

    items = raw if isinstance(raw, list) else (raw.get("cameras") or raw.get("data") or [])
    cams = []
    for c in items:
        site = c.get("site") or {}
        lat = site.get("latitude")
        lng = site.get("longitude")
        if lat is None or lng is None:
            continue
        img = (c.get("image") or {}).get("url") or ""
        cams.append({
            "name": c.get("name") or site.get("id") or "camera",
            "lat": round(float(lat), 5),
            "lng": round(float(lng), 5),
            "state": site.get("state") or "",
            "county": site.get("county") or "",
            "img": img,            # live-frame URL — hot-linked by the frontend, NOT re-hosted
            "src": c.get("source") or "AlertWest",
        })

    payload = {
        "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "count": len(cams),
        "source": "AlertWest / ALERTCalifornia (camera metadata only; imagery hot-linked, CC BY-NC-ND)",
        "cameras": cams,
    }
    os.makedirs(os.path.dirname(OUT_PATH), exist_ok=True)
    with open(OUT_PATH, "w") as f:
        json.dump(payload, f, separators=(",", ":"))
    # state breakdown for the log
    from collections import Counter
    by = Counter(c["state"] for c in cams)
    print(f"wrote {OUT_PATH}: {len(cams)} cameras — " +
          ", ".join(f"{s}:{n}" for s, n in by.most_common(8)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
