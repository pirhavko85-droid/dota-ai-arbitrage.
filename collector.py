import csv
import json
import os
import urllib.request
from datetime import datetime, timezone

URL = "https://api.opendota.com/api/proMatches"
req = urllib.request.Request(URL, headers={"User-Agent": "dota-ai-arbitrage-research/0.1"})
with urllib.request.urlopen(req, timeout=35) as response:
    matches = json.load(response)
if not isinstance(matches, list):
    raise RuntimeError("Unexpected API response")

os.makedirs("output", exist_ok=True)
stamp = datetime.now(timezone.utc).isoformat()
fields = ["match_id", "start_time", "duration", "radiant_team_id", "dire_team_id", "radiant_name", "dire_name", "radiant_win", "league_name"]
rows = [{key: m.get(key) for key in fields} for m in matches if isinstance(m, dict)]
with open("output/matches.csv", "w", encoding="utf-8", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=fields)
    writer.writeheader()
    writer.writerows(rows)
with open("output/snapshot.json", "w", encoding="utf-8") as f:
    json.dump({"collected_at_utc": stamp, "source": URL, "count": len(rows), "matches": rows}, f, ensure_ascii=False, indent=2)
print(f"Collected {len(rows)} professional match summaries at {stamp}")
