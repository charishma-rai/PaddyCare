import streamlit as st
from src.inference.predict import CLASS_NAMES
from src.knowledge.disease_info import INFO
from webapp import db, theme

user = st.session_state.user
theme.hero("History", "Every leaf check you have made, in one place.", eyebrow="Your records")

choice = st.selectbox("Show", ["All results"] + CLASS_NAMES)
rows = db.list_predictions(user["id"], None if choice == "All results" else choice)
if not rows:
    theme.note("Nothing here yet. Use Check a leaf to take your first photo.")
    st.stop()

st.caption(f"{len(rows)} check(s)")
for r in rows:
    with st.container(border=True):
        p = db.image_path(r["image"])
        if p:
            st.image(p, width=150)
        kind = "gold" if r["label"] != "Healthy" else "olive"
        st.markdown(theme.badge(r["label"], kind) + (theme.badge("Retake needed", "muted") if r["uncertain"] else ""),
                    unsafe_allow_html=True)
        st.caption(f"{round(r['confidence']*100)}% confidence, {db.time_ago(r['created'])}")
        with st.expander("Advice"):
            info = INFO[r["label"]]
            st.write(info["summary"])
            theme.bullets(info["do_now"])
        if st.button("Delete", key=f"del_{r['id']}"):
            db.delete_prediction(user["id"], r["id"])
            st.rerun()
