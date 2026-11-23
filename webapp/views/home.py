import streamlit as st
from webapp import db, theme

user = st.session_state.user
theme.hero(f"Hello, {user['name'].split()[0]}", "Check a leaf, review your history, or reach the community.", eyebrow="Welcome back")

n_checks, n_posts = db.counts(user["id"])
theme.stats([(n_checks, "Leaf checks"), (n_posts, "Your posts")])

st.page_link("views/predict.py", label="Check a leaf", icon=":material/photo_camera:", width="stretch")
st.page_link("views/community.py", label="Ask for help, sell or find a buyer", icon=":material/groups:", width="stretch")
st.page_link("views/history.py", label="Previous checks", icon=":material/history:", width="stretch")
st.page_link("views/info.py", label="Prices, MSP and government schemes", icon=":material/account_balance:", width="stretch")
st.page_link("views/account.py", label="Account and sign out", icon=":material/person:", width="stretch")

theme.section("Recent checks")
recent = db.list_predictions(user["id"])[:3]
if not recent:
    st.caption("No checks yet. Take a photo of a leaf to start.")
for r in recent:
    with st.container(border=True):
        p = db.image_path(r["image"])
        if p:
            st.image(p, width=110)
        st.markdown(theme.badge(r["label"], "olive" if r["label"] == "Healthy" else "gold")
                    + (theme.badge("Retake", "muted") if r["uncertain"] else ""), unsafe_allow_html=True)
        st.caption(f"{round(r['confidence']*100)}% confidence, {db.time_ago(r['created'])}")

theme.section("Latest in the community")
posts = db.list_posts(limit=3)
if not posts:
    st.caption("No posts yet. Be the first to post in the Community tab.")
for p in posts:
    with st.container(border=True):
        st.markdown(theme.badge(p["kind"]) + theme.badge(p["author_role"], "muted"), unsafe_allow_html=True)
        st.markdown(f"**{p['title']}**")
        st.caption(f"{p['author']}, {p['district'] or 'no location'}, {db.time_ago(p['created'])}")
