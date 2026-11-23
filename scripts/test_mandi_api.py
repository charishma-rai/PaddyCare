"""Run once after you get your data.gov.in key:

    set DATA_GOV_API_KEY=your-key        (Windows cmd)
    export DATA_GOV_API_KEY=your-key     (Mac/Linux)
    python scripts/test_mandi_api.py

It prints how many records came back and a few Karnataka paddy rows, so you know the live prices will work.
"""
import json, os, sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parents[1]))
from webapp.services import mandi

key = os.environ.get("DATA_GOV_API_KEY")
if not key:
    sys.exit("Set DATA_GOV_API_KEY first (see the comment at the top of this file).")
res = os.environ.get("DATA_GOV_RESOURCE_ID", mandi.DEFAULT_RESOURCE)
for extra in ({"filters[state.keyword]": "Karnataka"}, {"filters[state]": "Karnataka"}, {}):
    try:
        data = mandi._request(res, {"api-key": key, "format": "json", "limit": 1000, **extra})
        recs = data.get("records") or []
        print(f"filter {extra or 'none'}: {len(recs)} records; fields: {list(recs[0].keys()) if recs else '-'}")
        rows = mandi.parse_records(recs, "Karnataka")
        print(f"  Karnataka paddy rows: {len(rows)}")
        for r in rows[:5]:
            print("  ", r)
        if recs: break
    except Exception as e:
        print(f"filter {extra or 'none'}: FAILED -> {e}")
