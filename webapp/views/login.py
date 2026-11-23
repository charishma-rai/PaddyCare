import streamlit as st
from webapp import db, theme

theme.hero(theme.APP_NAME, "Early, reliable paddy leaf diagnosis, with a community that can help.",
           eyebrow="Paddy leaf health", big=True)

tab_in, tab_new = st.tabs(["Sign in", "Create account"])

with tab_in:
    with st.form("signin"):
        u = st.text_input("Username")
        p = st.text_input("Password", type="password")
        go = st.form_submit_button("Sign in", type="primary", width="stretch")
    if go:
        user = db.authenticate(u, p)
        if user:
            st.session_state.user = user
            st.rerun()
        else:
            st.error("Username or password is not correct.")

with tab_new:
    with st.form("signup"):
        name = st.text_input("Full name")
        role = st.selectbox("I am a", db.ROLES)
        c1, c2 = st.columns(2)
        district = c1.text_input("District", value="Dakshina Kannada")
        phone = c2.text_input("Phone (optional)", help="Shown to others only if you choose to share it on a post.")
        username = st.text_input("Username")
        pw = st.text_input("Password", type="password", help="At least 6 characters.")
        pw2 = st.text_input("Repeat password", type="password")
        make = st.form_submit_button("Create account", type="primary", width="stretch")
    if make:
        if pw != pw2:
            st.error("The two passwords do not match.")
        else:
            ok, msg = db.create_user(name, username, pw, role, district, phone)
            if ok:
                st.session_state.user = db.authenticate(username, pw)
                st.rerun()
            else:
                st.error(msg)

theme.section("What you can do")
st.markdown("""<div class="feats">
<div><b>Diagnose</b><span>Photograph a leaf and get a result with clear next steps.</span></div>
<div><b>Track</b><span>Keep every check in one history you can come back to.</span></div>
<div><b>Connect</b><span>Reach experts, farmers and buyers near you.</span></div></div>""", unsafe_allow_html=True)
