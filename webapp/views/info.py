import json
import statistics
from pathlib import Path

import streamlit as st

from webapp import theme
from webapp.services import mandi

user = st.session_state.user
INFO = json.loads((Path(__file__).resolve().parents[1] / "data" / "gov_info.json").read_text(encoding="utf-8"))

theme.hero("Farmer info", "Prices, support prices and government schemes for paddy farmers.", eyebrow="Government resources")


def verified(item):
    v = item.get("verified_on")
    return f"Checked {v}" if v else "Not yet verified by our team"


# ---------------------------------------------------------------- MSP
msp = INFO["msp"]
theme.section("Minimum support price (paddy)")
theme.stats([(f"\u20b9{msp['common_per_quintal']:,}", "Common, per quintal"),
             (f"\u20b9{msp['grade_a_per_quintal']:,}", "Grade A, per quintal")])
st.caption(f"{msp['season']}. {msp['note']} ({verified(msp)})")

# ---------------------------------------------------------------- live prices
theme.section("Market prices near you")
c1, c2 = st.columns(2)
state = c1.text_input("State", value="Karnataka")
district = c2.text_input("District (optional)", value=user.get("district") or "")

res = mandi.get_prices(state, district)
if res["error"] == "no_key":
    theme.note("Live prices are not set up yet. Get a free API key at data.gov.in and add it to "
               ".streamlit/secrets.toml as DATA_GOV_API_KEY. See the README for the steps.")
elif not res["rows"]:
    theme.note("No paddy prices found for this state and district right now. Try clearing the district, "
               "or check again later. Not every market reports paddy every day.")
    if res["error"]:
        st.caption(f"Technical detail: {res['error']}")
else:
    rows = res["rows"]
    modal = statistics.median(r["modal"] for r in rows)
    diff = modal - msp["common_per_quintal"]
    theme.stats([(f"\u20b9{modal:,.0f}", "Typical market price (modal), per quintal"),
                 (f"{'+' if diff >= 0 else '-'}\u20b9{abs(diff):,.0f}", "Compared with common MSP")])
    st.dataframe(
        [{"Market": r["market"], "District": r["district"], "Variety": r["variety"], "Date": r["date"],
          "Min": r["min"], "Max": r["max"], "Modal": r["modal"]} for r in rows[:60]],
        hide_index=True, width="stretch")
    when = "Live data" if res["source"] == "live" else "Saved data (the live service could not be reached)"
    st.caption(f"{when}, updated {res['updated']}. Prices are per quintal. Source: Agmarknet via data.gov.in "
               "(Government Open Data License, India). Prices differ by variety and grade, so treat the MSP "
               "comparison as a rough guide.")

# ---------------------------------------------------------------- schemes
theme.section("Schemes and support")
for s in INFO["schemes"]:
    with st.expander(s["name"]):
        st.write(s["summary"])
        if s.get("url"):
            st.link_button("Open official site", s["url"])
        st.caption(verified(s) + ". Check eligibility and dates on the official site before you apply.")

# ---------------------------------------------------------------- help
theme.section("Local help")
for h in INFO["help"]:
    with st.container(border=True):
        st.markdown(f"**{h['name']}**")
        st.write(h["address"])
        st.caption((f"Phone: {h['phone']}" if h.get("phone") else "Phone not added yet. Confirm it on the official page.")
                   + f"  |  {verified(h)}")

theme.note("This page is information only. Always confirm details with your local agriculture office or Krishi Vigyan Kendra.")
