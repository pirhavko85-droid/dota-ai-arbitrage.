"""Descriptive baseline only: no betting profitability claims without timestamped odds."""
import csv
import json
import statistics
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

source = Path("output/snapshot.json")
payload = json.loads(source.read_text(encoding="utf-8"))
rows = payload["matches"]
valid = [m for m in rows if isinstance(m.get("duration"), (int, float)) and m["duration"] > 0 and isinstance(m.get("radiant_win"), bool)]
duration_minutes = [m["duration"] / 60 for m in valid]
leagues = Counter(str(m.get("league_name") or "Unknown") for m in rows)
report = {
    "generated_utc": datetime.now(timezone.utc).isoformat(),
    "source": payload["source"],
    "snapshot_size": len(rows),
    "valid_completed_matches": len(valid),
    "radiant_win_rate": round(sum(m["radiant_win"] for m in valid) / len(valid), 4) if valid else None,
    "median_duration_minutes": round(statistics.median(duration_minutes), 2) if valid else None,
    "leagues_top_10": leagues.most_common(10),
    "limitations": [
        "The proMatches endpoint is a recent snapshot, not a representative full-season sample.",
        "Draft, in-game gold/xp timelines and synchronized bookmaker odds are not present.",
        "No profitable arbitrage or predictive edge can be inferred from this report."
    ]
}
Path("output/baseline_report.json").write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
print(json.dumps(report, ensure_ascii=False, indent=2))
