import streamlit as st
from webapp import db, theme

user = st.session_state.user
theme.hero("Account", "Your details and sign out.", eyebrow="Profile")
st.markdown(theme.badge(user["role"], "green"), unsafe_allow_html=True)
st.write(f"**{user['name']}**  (@{user['username']})")

with st.form("profile"):
    district = st.text_input("District", value=user.get("district") or "")
    phone = st.text_input("Phone", value=user.get("phone") or "",
                          help="Shown on a post only if you tick 'Show my phone number'.")
    save = st.form_submit_button("Save changes", type="primary", width="stretch")
if save:
    db.update_profile(user["id"], district, phone)
    st.session_state.user = {**user, "district": district.strip(), "phone": phone.strip()}
    st.success("Saved.")

if st.button("Sign out", width="stretch"):
    st.session_state.clear()
    st.rerun()
