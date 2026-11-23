"""Daily paddy market (mandi) prices from the official Open Government Data platform (data.gov.in).

Needs a free API key from data.gov.in. Put it in .streamlit/secrets.toml as
    DATA_GOV_API_KEY = "your-key"
or set the environment variable DATA_GOV_API_KEY.

If the API is down or no key is set, the page keeps working: it shows the last
saved prices (if any) or a friendly message. Run scripts/test_mandi_api.py once
to check that your key and the resource id work.
"""
import datetime as dt
import json
import os
import urllib.parse
import urllib.request

import streamlit as st

from webapp import db

BASE = "https://api.data.gov.in/resource/"
DEFAULT_RESOURCE = "35985678-0d79-46b4-9ed6-6f13308a1d24"   # Agmarknet daily mandi prices (change here or via DATA_GOV_RESOURCE_ID)


def _secret(name, default=None):
    try:
        v = st.secrets.get(name)
    except Exception:
        v = None
    return v or os.environ.get(name) or default


def get_api_key():
    return _secret("DATA_GOV_API_KEY")


def get_resource_id():
    return _secret("DATA_GOV_RESOURCE_ID", DEFAULT_RESOURCE)


# ---------- parsing (pure functions, easy to test) ----------
def _num(v):
    try:
        return float(str(v).replace(",", "").strip())
    except (TypeError, ValueError):
        return None


def normalize(rec):
    r = {str(k).strip().lower().replace("_x0020_", "_").replace(" ", "_"): v for k, v in rec.items()}

    def pick(*names):
        for n in names:
            if r.get(n) not in (None, ""):
                return r[n]
        return None

    return {"state": pick("state"), "district": pick("district"), "market": pick("market"),
            "commodity": pick("commodity"), "variety": pick("variety"),
            "date": pick("arrival_date", "date"),
            "min": _num(pick("min_price")), "max": _num(pick("max_price")), "modal": _num(pick("modal_price"))}


def _date_key(s):
    for fmt in ("%d/%m/%Y", "%Y-%m-%d", "%d-%m-%Y"):
        try:
            return dt.datetime.strptime(str(s), fmt)
        except ValueError:
            pass
    return dt.datetime.min


def parse_records(records, state=None, district=None, keyword="paddy"):
    rows = [normalize(r) for r in records]
    rows = [r for r in rows if r["commodity"] and keyword in str(r["commodity"]).lower() and r["modal"] is not None]
    if state:
        rows = [r for r in rows if str(r["state"] or "").lower() == state.strip().lower()]
    if district and district.strip():
        rows = [r for r in rows if district.strip().lower() in str(r["district"] or "").lower()]
    return sorted(rows, key=lambda r: _date_key(r["date"]), reverse=True)


# ---------- network ----------
def _request(resource, params):
    url = BASE + resource + "?" + urllib.parse.urlencode(params)
    req = urllib.request.Request(url, headers={"User-Agent": "PaddyCare/1.0"})
    with urllib.request.urlopen(req, timeout=20) as resp:
        return json.load(resp)


@st.cache_data(ttl=6 * 3600, show_spinner=False)
def _fetch_raw(api_key, resource, state):
    """Cached for 6 hours. Raises on failure so errors are never cached."""
    last = None
    for extra in ({"filters[state.keyword]": state}, {"filters[state]": state}, {}):
        try:
            data = _request(resource, {"api-key": api_key, "format": "json", "limit": 1000, **extra})
            if data.get("records"):
                return data["records"]
        except Exception as e:   # try the next filter style
            last = e
    raise RuntimeError(f"no records returned ({last or 'empty response'})")


def _cache_path():
    return db.APP_DIR / "mandi_cache.json"


def get_prices(state="Karnataka", district=""):
    """Returns {rows, source: 'live'|'saved'|None, updated, error}."""
    key = get_api_key()
    if not key:
        return {"rows": [], "source": None, "updated": None, "error": "no_key"}
    try:
        records = _fetch_raw(key, get_resource_id(), state)
        db.APP_DIR.mkdir(parents=True, exist_ok=True)
        _cache_path().write_text(json.dumps({"saved": dt.datetime.now().isoformat(timespec="minutes"),
                                             "state": state, "records": records}))
        return {"rows": parse_records(records, state, district), "source": "live",
                "updated": dt.datetime.now().strftime("%d %b %Y, %H:%M"), "error": None}
    except Exception as e:
        try:
            saved = json.loads(_cache_path().read_text())
            if saved.get("state") == state:
                return {"rows": parse_records(saved["records"], state, district), "source": "saved",
                        "updated": saved["saved"], "error": str(e)}
        except Exception:
            pass
        return {"rows": [], "source": None, "updated": None, "error": str(e)}
