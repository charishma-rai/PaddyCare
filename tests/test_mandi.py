import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parents[1]))
from webapp.services import mandi

SAMPLE = [
    {"State": "Karnataka", "District": "Udupi", "Market": "Udupi", "Commodity": "Paddy(Dhan)(Common)", "Variety": "Other",
     "Arrival_Date": "05/10/2026", "Min_Price": "2300", "Max_Price": "2500", "Modal_Price": "2400"},
    {"state": "Karnataka", "district": "Mangalore", "market": "Mangalore", "commodity": "Paddy(Dhan)(Common)",
     "arrival_date": "06/10/2026", "min_price": "2350", "max_price": "2600", "modal_price": "2450"},
    {"state": "Karnataka", "district": "Udupi", "market": "Udupi", "commodity": "Tomato", "modal_price": "900"},
    {"state": "Kerala", "district": "Thrissur", "market": "X", "commodity": "Paddy(Dhan)(Common)", "modal_price": "2500"},
    {"state": "Karnataka", "district": "Udupi", "market": "Udupi", "commodity": "Paddy(Dhan)(Common)", "modal_price": "NA"},
]


def test_parse():
    rows = mandi.parse_records(SAMPLE, "Karnataka")
    assert len(rows) == 2 and rows[0]["market"] == "Mangalore"          # newest first, only paddy, only Karnataka, bad price dropped
    assert [r["modal"] for r in mandi.parse_records(SAMPLE, "Karnataka", "udupi")] == [2400.0]


if __name__ == "__main__":
    test_parse(); print("mandi tests passed")
