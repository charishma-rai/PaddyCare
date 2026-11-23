import hashlib

import streamlit as st
from PIL import Image, ImageOps

from src.inference.predict import predict, CONFIDENCE_THRESHOLD
from src.knowledge.disease_info import INFO, SEEK_HELP, TREATMENT_NOTE
from webapp import db, theme

user = st.session_state.user
theme.hero("Check a leaf", "Take a photo or upload one. We look for common paddy diseases.", eyebrow="Diagnosis")
theme.chips(["One leaf, filling the frame", "Natural daylight", "Hold the phone steady"])

tab_cam, tab_up = st.tabs(["Take a photo", "Upload a photo"])
with tab_cam:
    cam = st.camera_input("Point the camera at a leaf", label_visibility="collapsed")
with tab_up:
    up = st.file_uploader("Choose a photo", type=["jpg", "jpeg", "png"],
                          help="On a phone this also lets you open the camera app.")

source = cam or up
if source is None:
    theme.note("Take or upload a photo to start.")
    st.stop()

raw = source.getvalue()
key = hashlib.md5(raw).hexdigest()
image = ImageOps.exif_transpose(Image.open(source)).convert("RGB")
image.thumbnail((1024, 1024))

if st.session_state.get("res_key") != key:
    for k in ("res", "res_img"):
        st.session_state.pop(k, None)

if st.button("Check this leaf", type="primary", width="stretch"):
    try:
        with st.spinner("Checking the leaf..."):
            r = predict(image)
    except (FileNotFoundError, RuntimeError) as exc:
        st.error(str(exc))
        st.stop()
    img_name = db.save_image(image)
    db.add_prediction(user["id"], r["label"], r["confidence"], r["uncertain"], img_name)
    st.session_state.update(res=r, res_key=key, res_img=img_name)

r = st.session_state.get("res") if st.session_state.get("res_key") == key else None
if r is None:
    st.image(image, caption="Your photo", width="stretch")
    st.stop()

label, info = r["label"], INFO[r["label"]]
state = "retake" if r["uncertain"] else ("healthy" if label == "Healthy" else "disease")
theme.diagnosis_band(label, r["confidence"], state)

view = st.segmented_control("View", ["Your photo", "Where the model looked"], default="Your photo",
                            label_visibility="collapsed", key="viewmode", width="stretch")
if view == "Where the model looked":
    if r.get("heatmap") is not None:
        st.image(r["heatmap"], caption="Highlighted areas influenced the result most. This is not proof of a correct diagnosis.", width="stretch")
    else:
        st.info("Visual explanations (Grad-CAM) are not available yet. The prediction itself comes from the trained MobileNetV2 model.")
else:
    st.image(image, width="stretch")

if state == "retake":
    for issue in r["quality"]["issues"]:
        st.warning(issue)
    if r["quality"]["ok"]:
        st.warning(f"The model is not confident (below {round(CONFIDENCE_THRESHOLD*100)}%). "
                   "Take another photo of a single leaf, closer and in better light.")
    st.caption("This check was saved to your history so you can compare it with your next photo.")
    with st.expander(f"Read about {label} anyway"):
        st.write(info["summary"])
else:
    st.write(info["summary"])
    tabs = st.tabs(["Signs", "What to do now", "Treatment", "Prevention"] if label != "Healthy"
                   else ["Signs", "What to do now", "Prevention"])
    with tabs[0]:
        theme.bullets(info["signs"])
        if info["causes"]:
            st.markdown("**Why it happens**")
            theme.bullets(info["causes"])
    with tabs[1]:
        theme.bullets(info["do_now"])
    if label != "Healthy":
        with tabs[2]:
            theme.bullets(info["treatment"])
            theme.note(TREATMENT_NOTE)
    with tabs[-1]:
        theme.bullets(info["prevention"])
    if label != "Healthy":
        theme.note(SEEK_HELP)

with st.expander("All probabilities"):
    for name, p in sorted(r["probs"].items(), key=lambda kv: -kv[1]):
        st.write(f"{name}: {round(p*100)}%")
        st.progress(float(p))

theme.section("Need help with this?")
with st.form("ask_help"):
    msg = st.text_area("Tell people what you see", placeholder="When did it start? How much of the field is affected?")
    district = st.text_input("Your district", value=user.get("district") or "")
    share = st.checkbox("Show my phone number on this post", value=False, disabled=not user.get("phone"),
                        help=None if user.get("phone") else "Add a phone number in Account first.")
    send = st.form_submit_button("Post to the community", width="stretch")
if send:
    if len(msg.strip()) < 5:
        st.error("Please write a few words about the problem.")
    else:
        db.add_post(user["id"], "Need help", f"Help with {label} in my paddy", msg, district, share,
                    db.copy_image(st.session_state.get("res_img")), f"{label} ({round(r['confidence']*100)}%)")
        st.success("Posted. You can see replies in the Community tab.")

if r.get("demo"):
    st.caption("Demo mode: results are placeholders until the trained model is connected.")
