"""Fetch a small reproducible sample of completed professional match details.
OpenDota match details may be unparsed; missing timeline fields are recorded, not invented.
"""
import json
import os
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

src = json.loads(Path("output/snapshot.json").read_text(encoding="utf-8"))
matches = src.get("matches", [])
limit = max(1, min(int(os.getenv("DETAIL_LIMIT", "5")), 10))
out = []
for m in matches:
    match_id = m.get("match_id")
    if not isinstance(match_id, int):
        continue
    url = f"https://api.opendota.com/api/matches/{match_id}"
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "dota-ai-arbitrage-research/0.2"})
        with urllib.request.urlopen(req, timeout=30) as response:
            detail = json.load(response)
        players = detail.get("players") or []
        picks = [{"hero_id": p.get("hero_id"), "is_radiant": p.get("isRadiant"),
                  "lane_role": p.get("lane_role")} for p in players if p.get("hero_id")]
        out.append({"match_id": match_id, "status": "ok", "start_time": detail.get("start_time"),
                    "duration": detail.get("duration"), "radiant_win": detail.get("radiant_win"),
                    "patch": detail.get("patch"), "picks": picks,
                    "picks_complete": len(picks) == 10,
                    "radiant_gold_adv": detail.get("radiant_gold_adv"),
                    "radiant_xp_adv": detail.get("radiant_xp_adv")})
    except (urllib.error.URLError, TimeoutError, ValueError) as exc:
        out.append({"match_id": match_id, "status": "error", "error": str(exc)[:200]})
    if len(out) >= limit:
        break
    time.sleep(1.2)
Path("output/match_details.json").write_text(json.dumps({
    "collected_at_utc": datetime.now(timezone.utc).isoformat(),
    "sample_limit": limit, "matches": out,
    "note": "Small nonrepresentative connectivity and schema sample; not a strategy backtest."
}, ensure_ascii=False, indent=2), encoding="utf-8")
print(f"Details: {sum(m['status']=='ok' for m in out)}/{len(out)} successful; complete drafts: {sum(m.get('picks_complete',False) for m in out)}")
