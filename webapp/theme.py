"""Look and feel. Palette: Flax, Gold, Olivine, Cal Poly green, Taupe.

Contains the animated paddy illustration (an SVG with built-in sway animation)
and small HTML helpers used by every page.
"""
import base64
import html
import math
from functools import lru_cache

import streamlit as st

APP_NAME = "PaddyCare"   # placeholder name - the team can rename it
FLAX, GOLD, OLIVINE, GREEN, TAUPE, IVORY = "#F8EC99", "#DEB938", "#A8B774", "#2C4219", "#433A30", "#FAF6E3"
GREEN_LIGHT = "#375225"   # slightly lighter green for gradients

# ------------------------------------------------------------------ CSS
CSS = f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,500;9..144,600&family=Inter:wght@400;500;600&display=swap');

/* --- layout: keep content clear of Streamlit's top bar so the title is never cut off --- */
header[data-testid="stHeader"] {{background:{IVORY}; border-bottom:1px solid rgba(67,58,48,.10);}}
[data-testid="stAppDeployButton"], [data-testid="stMainMenu"], [data-testid="stDecoration"], #MainMenu, footer {{display:none !important;}}
.stMainBlockContainer, .block-container {{max-width:720px; padding:5.2rem 1.1rem 4rem !important;}}

/* --- type --- */
.stApp, .stApp p, .stApp li, .stApp label, .stApp button, .stApp input, .stApp textarea
  {{font-family:'Inter',system-ui,-apple-system,'Segoe UI',sans-serif;}}
.stApp h1, .stApp h2, .stApp h3 {{font-family:'Fraunces',Georgia,'Times New Roman',serif !important; color:{GREEN}; font-weight:600; letter-spacing:-.01em;}}
.stApp label p {{font-size:.84rem; font-weight:500; color:{TAUPE}; letter-spacing:.01em;}}

/* --- hero --- */
.hero {{position:relative; background:linear-gradient(135deg,{GREEN} 0%,{GREEN_LIGHT} 100%); color:{FLAX};
  border-radius:16px; padding:1.5rem 1.5rem 1.6rem; margin:0 0 1.4rem; overflow:hidden; min-height:150px;
  box-shadow:0 10px 30px -14px rgba(44,66,25,.55);}}
.hero::after {{content:""; position:absolute; left:1.5rem; right:1.5rem; bottom:0; height:1px; background:linear-gradient(90deg,{GOLD},rgba(222,185,56,0));}}
.hero .txt {{position:relative; z-index:2;}}
.hero .eyebrow {{font-size:.68rem; letter-spacing:.2em; text-transform:uppercase; color:{GOLD}; font-weight:600; margin-bottom:.55rem;}}
.hero .title {{font-family:'Fraunces',Georgia,serif; font-weight:600; font-size:clamp(1.6rem,7vw,2.2rem); line-height:1.12; color:{FLAX}; letter-spacing:-.015em; white-space:nowrap;}}
.hero .sub {{margin-top:.55rem; font-size:.9rem; line-height:1.5; color:rgba(248,236,153,.8); max-width:58%;}}
.hero img.art {{position:absolute; right:.6rem; bottom:-8px; height:118px; width:auto; z-index:1; opacity:.95;}}
.hero.big {{min-height:215px;}}
.hero.big .title {{font-size:clamp(2rem,9vw,2.6rem);}}
.hero.big .sub {{max-width:55%;}}
.hero.big img.art {{height:150px; right:.4rem; bottom:-10px;}}

/* --- section headings --- */
.sec {{display:flex; align-items:center; gap:.8rem; margin:1.8rem 0 .8rem;}}
.sec span {{font-size:.72rem; letter-spacing:.16em; text-transform:uppercase; font-weight:600; color:{GREEN}; white-space:nowrap;}}
.sec::after {{content:""; flex:1; height:1px; background:rgba(67,58,48,.16);}}

/* --- tags, chips, notes --- */
.badge {{display:inline-block; padding:.18rem .5rem; border-radius:4px; font-size:.66rem; font-weight:600; letter-spacing:.07em; text-transform:uppercase; margin:0 .35rem .3rem 0;}}
.badge.gold {{background:rgba(222,185,56,.28); color:#6b5410;}}
.badge.olive {{background:rgba(168,183,116,.38); color:{GREEN};}}
.badge.green {{background:{GREEN}; color:{FLAX};}}
.badge.muted {{background:transparent; border:1px solid rgba(67,58,48,.25); color:#6a5f52;}}
.chips {{display:flex; flex-wrap:wrap; gap:.45rem; margin:.2rem 0 1rem;}}
.chip {{font-size:.78rem; padding:.3rem .7rem; border:1px solid rgba(67,58,48,.2); border-radius:999px; background:#FFFEF7; color:{TAUPE};}}
.note {{background:#FFFEF7; border:1px solid rgba(67,58,48,.12); border-left:3px solid {GOLD}; padding:.8rem 1rem; border-radius:8px; color:{TAUPE}; font-size:.9rem; line-height:1.5; margin:.8rem 0;}}
.muted-txt {{color:#6a5f52; font-size:.85rem;}}

.feats {{display:grid; grid-template-columns:repeat(3,1fr); gap:.9rem;}}
.feats b {{display:block; font-family:'Fraunces',Georgia,serif; color:{GREEN}; font-size:1.05rem; margin-bottom:.2rem;}}
.feats span {{font-size:.8rem; line-height:1.45; color:#6a5f52;}}
/* --- stat tiles --- */
.stats {{display:grid; grid-template-columns:1fr 1fr; gap:.8rem; margin-bottom:1rem;}}
.stat {{background:#FFFEF7; border:1px solid rgba(67,58,48,.12); border-radius:12px; padding:.9rem 1.1rem; box-shadow:0 1px 2px rgba(67,58,48,.04);}}
.stat .num {{font-family:'Fraunces',Georgia,serif; font-size:2rem; font-weight:600; color:{GREEN}; line-height:1.1;}}
.stat .lbl {{font-size:.72rem; letter-spacing:.12em; text-transform:uppercase; color:#6a5f52; margin-top:.15rem;}}

/* --- diagnosis card --- */
.diag {{border-radius:16px; padding:1.3rem 1.4rem 1.2rem; margin:.4rem 0 1.2rem; box-shadow:0 12px 30px -16px rgba(44,66,25,.5);}}
.diag .eyebrow {{font-size:.68rem; letter-spacing:.2em; text-transform:uppercase; font-weight:600; opacity:.85;}}
.diag .dname {{font-family:'Fraunces',Georgia,serif; font-size:clamp(1.8rem,8vw,2.4rem); font-weight:600; line-height:1.1; margin:.3rem 0 .9rem;}}
.diag .row {{display:flex; align-items:baseline; gap:.5rem; margin-bottom:.45rem;}}
.diag .big {{font-family:'Fraunces',Georgia,serif; font-size:1.5rem; font-weight:600;}}
.diag .cap {{font-size:.8rem; opacity:.85;}}
.meter {{height:4px; border-radius:99px; background:rgba(255,255,255,.22); overflow:hidden;}}
.meter > span {{display:block; height:100%; background:{GOLD}; border-radius:99px;}}
.diag.disease {{background:linear-gradient(135deg,{GREEN},{GREEN_LIGHT}); color:{FLAX};}}
.diag.disease .eyebrow {{color:{GOLD};}}
.diag.healthy {{background:linear-gradient(135deg,#B7C583,{OLIVINE}); color:{GREEN};}}
.diag.healthy .meter {{background:rgba(44,66,25,.2);}} .diag.healthy .meter > span {{background:{GREEN};}}
.diag.retake {{background:#FFFEF7; color:{TAUPE}; border:1px solid rgba(222,185,56,.7); border-left:4px solid {GOLD}; box-shadow:none;}}
.diag.retake .eyebrow {{color:#8a6d0c;}}
.diag.retake .dname {{color:{GREEN}; font-size:1.7rem;}}
.diag.retake .meter {{background:rgba(67,58,48,.12);}}

/* --- Streamlit widgets --- */
div[data-baseweb="input"], div[data-baseweb="base-input"], div[data-baseweb="input"] input, div[data-baseweb="textarea"], div[data-baseweb="textarea"] textarea, [data-testid="stTextInputRootElement"], [data-testid="stTextAreaRootElement"], [data-testid="stNumberInputContainer"], div[data-baseweb="select"] > div {{background:#FFFEF7 !important; border:1px solid rgba(67,58,48,.22) !important; border-radius:8px !important;}}
div[data-baseweb="base-input"] {{border:none !important;}}
div[data-baseweb="input"]:focus-within, div[data-baseweb="textarea"]:focus-within {{border-color:{GREEN} !important; box-shadow:0 0 0 3px rgba(44,66,25,.12);}}
.stButton button, .stFormSubmitButton button {{border-radius:8px; font-weight:600; letter-spacing:.02em; padding:.55rem 1rem; transition:all .15s ease;}}
.stButton button[kind="primary"], .stFormSubmitButton button[kind="primaryFormSubmit"], .stFormSubmitButton button[kind="primary"]
  {{background:{GREEN}; color:{FLAX}; border:1px solid {GREEN};}}
.stButton button[kind="primary"]:hover, .stFormSubmitButton button[kind="primaryFormSubmit"]:hover {{background:{GREEN_LIGHT}; color:#fff; box-shadow:0 6px 16px -8px rgba(44,66,25,.7);}}
.stButton button[kind="secondary"], .stFormSubmitButton button[kind="secondaryFormSubmit"] {{background:transparent; color:{GREEN}; border:1px solid rgba(44,66,25,.45);}}
.stButton button[kind="secondary"]:hover, .stFormSubmitButton button[kind="secondaryFormSubmit"]:hover {{background:rgba(44,66,25,.06); border-color:{GREEN}; color:{GREEN};}}
button[data-baseweb="tab"] {{font-weight:500; padding-left:.2rem; padding-right:.2rem; margin-right:1.2rem;}}
button[data-baseweb="tab"][aria-selected="true"] {{color:{GREEN}; font-weight:600;}}
div[data-baseweb="tab-highlight"] {{background:{GOLD} !important; height:3px !important;}}
div[data-baseweb="tab-border"] {{background:rgba(67,58,48,.14) !important;}}
[data-testid="stVerticalBlockBorderWrapper"] {{background:#FFFEF7; border-radius:12px !important; border-color:rgba(67,58,48,.13) !important; box-shadow:0 1px 3px rgba(67,58,48,.05);}}
[data-testid="stForm"] {{background:#FFFEF7; border:1px solid rgba(67,58,48,.13); border-radius:12px;}}
[data-testid="stPageLink"] {{width:100%;}}
a[data-testid="stPageLink-NavLink"] {{display:flex; width:100%; background:#FFFEF7; border:1px solid rgba(67,58,48,.13); border-radius:10px; padding:.7rem .9rem; margin-bottom:.45rem; transition:all .15s ease;}}
a[data-testid="stPageLink-NavLink"]:hover {{border-color:{GREEN}; background:#fff; transform:translateY(-1px); box-shadow:0 6px 14px -10px rgba(44,66,25,.6);}}
a[data-testid="stPageLink-NavLink"] p {{font-weight:500; color:{GREEN};}}
[data-testid="stExpander"] details {{background:#FFFEF7; border-color:rgba(67,58,48,.13); border-radius:10px;}}
[data-testid="stImage"] img {{border-radius:10px;}}
[data-testid="stAlert"] {{border-radius:10px;}}
.st-key-mainnav [data-testid="stButtonGroup"] {{width:100%; margin-bottom:.9rem;}}
.st-key-mainnav [data-testid="stButtonGroup"] > div {{width:100%; flex-wrap:nowrap !important; gap:0;}}
.st-key-mainnav [data-testid="stButtonGroup"] button {{flex:1 1 0; min-width:0; font-size:.8rem !important; font-weight:500; padding:.5rem .2rem !important; white-space:nowrap; background:#FFFEF7; border-color:rgba(67,58,48,.2); color:{TAUPE};}}
.st-key-mainnav [data-testid="stButtonGroup"] button[aria-checked="true"], .st-key-mainnav [data-testid="stButtonGroup"] button[aria-pressed="true"], .st-key-mainnav [data-testid="stButtonGroup"] button[kind="segmented_controlActive"]
  {{background:{GREEN} !important; color:{FLAX} !important; border-color:{GREEN} !important;}}
[data-testid="stFileUploaderDropzone"], [data-testid="stCameraInput"] > div, [data-testid="stCameraInputWebcamStyledBox"] {{background:#FFFEF7 !important; border:1px dashed rgba(44,66,25,.4) !important; border-radius:10px !important;}}
[data-testid="stFileUploaderFile"] {{background:transparent;}}
@media (prefers-reduced-motion: reduce) {{ .hero img.art {{animation:none;}} }}
</style>
"""


def inject_css():
    st.markdown(CSS, unsafe_allow_html=True)


# ------------------------------------------------ animated paddy illustration
def _bez(p0, p1, p2, p3, t):
    u = 1 - t
    x = u**3*p0[0] + 3*u*u*t*p1[0] + 3*u*t*t*p2[0] + t**3*p3[0]
    y = u**3*p0[1] + 3*u*u*t*p1[1] + 3*u*t*t*p2[1] + t**3*p3[1]
    dx = 3*u*u*(p1[0]-p0[0]) + 6*u*t*(p2[0]-p1[0]) + 3*t*t*(p3[0]-p2[0])
    dy = 3*u*u*(p1[1]-p0[1]) + 6*u*t*(p2[1]-p1[1]) + 3*t*t*(p3[1]-p2[1])
    return x, y, math.degrees(math.atan2(dy, dx))


def _stalk(x, height, lean, sway, dur, begin):
    base = (x, 232)
    top = (x + lean, 232 - height)
    c1, c2 = (x + lean * 0.1, 232 - height * 0.45), (x + lean * 0.9, 232 - height * 0.7)
    stem = f'<path d="M{base[0]} {base[1]} C{c1[0]:.1f} {c1[1]:.1f} {c2[0]:.1f} {c2[1]:.1f} {top[0]:.1f} {top[1]:.1f}" stroke="#A8B774" stroke-width="2.4" fill="none" stroke-linecap="round"/>'
    leaves = ""
    for t, side, ln in ((0.28, -1, 44), (0.5, 1, 38), (0.68, -1, 28)):
        px, py, _ = _bez(base, c1, c2, top, t)
        ex, ey = px + side * ln, py - ln * 0.55
        leaves += (f'<path d="M{px:.1f} {py:.1f} Q{px + side*ln*0.55:.1f} {py - ln*0.75:.1f} {ex:.1f} {ey + 10:.1f} '
                   f'Q{px + side*ln*0.4:.1f} {py - ln*0.2:.1f} {px:.1f} {py:.1f}Z" fill="#8FA05C" opacity=".95"/>')
    # drooping grain head (panicle)
    k0 = top
    k1, k2 = (top[0] + 18, top[1] - 16), (top[0] + 36, top[1] + 4)
    k3 = (top[0] + 34, top[1] + 44)
    branch = f'<path d="M{k0[0]:.1f} {k0[1]:.1f} C{k1[0]:.1f} {k1[1]:.1f} {k2[0]:.1f} {k2[1]:.1f} {k3[0]:.1f} {k3[1]:.1f}" stroke="#C9B24A" stroke-width="1.6" fill="none" stroke-linecap="round"/>'
    grains = ""
    for i in range(11):
        t = 0.12 + i * 0.082
        gx, gy, ang = _bez(k0, k1, k2, k3, t)
        for off, col in ((-3.4, "#DEB938"), (3.4, "#F8EC99")):
            nx, ny = -math.sin(math.radians(ang)), math.cos(math.radians(ang))
            grains += (f'<ellipse cx="{gx + nx*off:.1f}" cy="{gy + ny*off:.1f}" rx="2.7" ry="6" '
                       f'transform="rotate({ang + 90 + (8 if off > 0 else -8):.0f} {gx + nx*off:.1f} {gy + ny*off:.1f})" fill="{col}"/>')
    head_anim = (f'<animateTransform attributeName="transform" type="rotate" values="-4 {top[0]:.0f} {top[1]:.0f};5 {top[0]:.0f} {top[1]:.0f};-4 {top[0]:.0f} {top[1]:.0f}" '
                 f'dur="{dur*0.8:.1f}s" begin="{begin}s" repeatCount="indefinite" calcMode="spline" keySplines=".45 0 .55 1;.45 0 .55 1"/>')
    sway_anim = (f'<animateTransform attributeName="transform" type="rotate" values="{-sway} {x} 232;{sway} {x} 232;{-sway} {x} 232" '
                 f'dur="{dur}s" begin="{begin}s" repeatCount="indefinite" calcMode="spline" keySplines=".45 0 .55 1;.45 0 .55 1"/>')
    return f'<g>{stem}{leaves}<g>{branch}{grains}{head_anim}</g>{sway_anim}</g>'


@lru_cache(maxsize=1)
def paddy_art_uri():
    stalks = _stalk(70, 150, -10, 2.6, 5.4, 0) + _stalk(112, 188, 8, 2.2, 6.2, -1.2) + _stalk(154, 138, 12, 3.0, 4.8, -2.4)
    specks = "".join(
        f'<circle cx="{x}" cy="150" r="1.6" fill="#F8EC99" opacity="0">'
        f'<animate attributeName="cy" values="170;40" dur="{d}s" begin="{b}s" repeatCount="indefinite"/>'
        f'<animate attributeName="opacity" values="0;.7;0" dur="{d}s" begin="{b}s" repeatCount="indefinite"/></circle>'
        for x, d, b in ((40, 7, 0), (95, 8, 2), (176, 6.5, 4), (130, 9, 1)))
    water = ''.join(
        f'<path d="M-20 {y} q15 -4 30 0 t30 0 t30 0 t30 0 t30 0 t30 0 t30 0 t30 0 t30 0" stroke="#F8EC99" stroke-opacity="{o}" fill="none" stroke-width="1">'
        f'<animateTransform attributeName="transform" type="translate" values="0 0;30 0" dur="{d}s" repeatCount="indefinite"/></path>'
        for y, o, d in ((236, .35, 6), (244, .22, 8)))
    svg = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 224 250">{water}{specks}{stalks}</svg>')
    return "data:image/svg+xml;base64," + base64.b64encode(svg.encode()).decode()


# ------------------------------------------------------------------ helpers
def hero(title, sub="", eyebrow="", big=False):
    art = f'<img class="art" src="{paddy_art_uri()}" alt="">'
    eb = f'<div class="eyebrow">{html.escape(eyebrow)}</div>' if eyebrow else ""
    st.markdown(f'<div class="hero{" big" if big else ""}"><div class="txt">{eb}<div class="title">{html.escape(title)}</div>'
                f'<div class="sub">{html.escape(sub)}</div></div>{art}</div>', unsafe_allow_html=True)


def section(title):
    st.markdown(f'<div class="sec"><span>{html.escape(title)}</span></div>', unsafe_allow_html=True)


def badge(text, kind="gold"):
    return f'<span class="badge {kind}">{html.escape(text)}</span>'


def chips(items):
    st.markdown('<div class="chips">' + "".join(f'<span class="chip">{html.escape(i)}</span>' for i in items) + '</div>',
                unsafe_allow_html=True)


def note(text):
    st.markdown(f'<div class="note">{html.escape(text)}</div>', unsafe_allow_html=True)


def stats(pairs):
    st.markdown('<div class="stats">' + "".join(
        f'<div class="stat"><div class="num">{html.escape(str(n))}</div><div class="lbl">{html.escape(l)}</div></div>'
        for n, l in pairs) + '</div>', unsafe_allow_html=True)


def diagnosis_band(label, confidence, state):
    """state: 'disease' | 'healthy' | 'retake'"""
    pct = round(confidence * 100)
    eyebrow = "Result" if state != "retake" else "Photo needs a retake"
    name = label if state != "retake" else "Please retake the photo"
    cap = "confidence" if state != "retake" else f"confidence in best guess: {label}"
    st.markdown(f'''<div class="diag {state}"><div class="eyebrow">{eyebrow}</div>
        <div class="dname">{html.escape(name)}</div>
        <div class="row"><span class="big">{pct}%</span><span class="cap">{html.escape(cap)}</span></div>
        <div class="meter"><span style="width:{pct}%"></span></div></div>''', unsafe_allow_html=True)


def bullets(items):
    st.markdown("\n".join(f"- {it}" for it in items))
