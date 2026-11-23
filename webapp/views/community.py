import streamlit as st
from PIL import Image, ImageOps
from webapp import db, theme

user = st.session_state.user
theme.hero("Connect", "Ask for help, offer advice, sell your harvest or find a buyer.", eyebrow="Community")

KIND_HINT = {"Need help": "Ask other farmers and experts for advice.",
             "Offer help": "Share your knowledge or services.",
             "Sell produce": "List paddy or rice you want to sell.",
             "Want to buy": "Tell farmers what you want to buy."}


def render_post(p, mine_tab=False):
    with st.container(border=True):
        st.markdown(theme.badge(p["kind"]) + theme.badge(p["author_role"], "muted"), unsafe_allow_html=True)
        st.markdown(f"**{p['title']}**")
        st.caption(f"{p['author']}, {p['district'] or 'no location'}, {db.time_ago(p['created'])}")
        st.write(p["body"])
        path = db.image_path(p["image"])
        if path:
            st.image(path, width=260)
        if p["diagnosis"]:
            st.markdown(theme.badge("Model result: " + p["diagnosis"], "olive"), unsafe_allow_html=True)
        if p["contact"]:
            st.markdown(f"Phone: **{p['contact']}**")
        replies = db.list_replies(p["id"])
        with st.expander(f"Replies ({len(replies)})"):
            for r in replies:
                st.markdown(f"**{r['author']}** {theme.badge(r['author_role'], 'muted')}", unsafe_allow_html=True)
                st.write(r["body"])
            with st.form(f"reply_{p['id']}_{mine_tab}", clear_on_submit=True):
                text = st.text_area("Write a reply", key=f"rt_{p['id']}_{mine_tab}", label_visibility="collapsed",
                                    placeholder="Write a reply")
                if st.form_submit_button("Reply") and len(text.strip()) >= 2:
                    db.add_reply(p["id"], user["id"], text)
                    st.rerun()
        if p["user_id"] == user["id"] and st.button("Delete post", key=f"dp_{p['id']}_{mine_tab}"):
            db.delete_post(user["id"], p["id"])
            st.rerun()


tab_browse, tab_new, tab_mine = st.tabs(["Browse", "New post", "My posts"])

with tab_browse:
    kind = st.pills("Show", ["All"] + db.KINDS, default="All", label_visibility="collapsed")
    where = st.text_input("District", placeholder="Search by district, e.g. Udupi")
    posts = db.list_posts(None if kind in (None, "All") else kind, where or None)
    if not posts:
        theme.note("No posts match yet.")
    for p in posts:
        render_post(p)

with tab_new:
    with st.form("new_post"):
        k = st.selectbox("What do you want to do?", db.KINDS)
        st.caption(KIND_HINT[k])
        title = st.text_input("Title")
        body = st.text_area("Details")
        district = st.text_input("District", value=user.get("district") or "")
        photo = st.file_uploader("Add a photo (optional)", type=["jpg", "jpeg", "png"])
        share = st.checkbox("Show my phone number on this post", value=False, disabled=not user.get("phone"),
                            help=None if user.get("phone") else "Add a phone number in Account first.")
        go = st.form_submit_button("Post", type="primary", width="stretch")
    if go:
        if len(title.strip()) < 3 or len(body.strip()) < 5:
            st.error("Please add a title and a few details.")
        else:
            img = db.save_image(ImageOps.exif_transpose(Image.open(photo))) if photo else None
            db.add_post(user["id"], k, title, body, district, share, img)
            st.success("Posted.")

with tab_mine:
    mine = db.list_posts(user_id=user["id"])
    if not mine:
        theme.note("You have not posted yet.")
    for p in mine:
        render_post(p, mine_tab=True)
