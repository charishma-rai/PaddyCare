"""PaddyCare - entry point.   Run from the project root:  streamlit run webapp/app.py"""
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

import streamlit as st

from webapp import db, theme

st.set_page_config(page_title=theme.APP_NAME, page_icon="\U0001F33E", layout="centered",
                   initial_sidebar_state="collapsed")
db.init()
theme.inject_css()

if st.session_state.get("user"):
    pages = [
        st.Page("views/home.py", title="Home", icon=":material/home:", default=True),
        st.Page("views/predict.py", title="Check", icon=":material/photo_camera:"),
        st.Page("views/history.py", title="History", icon=":material/history:"),
        st.Page("views/community.py", title="Connect", icon=":material/groups:"),
        st.Page("views/info.py", title="Info", icon=":material/account_balance:"),
        st.Page("views/account.py", title="Account", icon=":material/person:"),
    ]
    nav = st.navigation(pages, position="hidden")   # we draw our own menu so it also works on phones
    by_title = {p.title: p for p in pages}
    menu = [t for t in by_title if t != "Account"]   # Account is reached from the Home page

    def _go():
        target = st.session_state.get("mainnav")
        if target and target != nav.title:
            st.switch_page(by_title[target])

    st.session_state["mainnav"] = nav.title if nav.title in menu else None
    st.segmented_control("Menu", menu, key="mainnav", on_change=_go,
                         label_visibility="collapsed", selection_mode="single", width="stretch")
else:
    nav = st.navigation([st.Page("views/login.py", title="Sign in")], position="hidden")
nav.run()
