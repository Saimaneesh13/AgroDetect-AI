import os
import io
import base64
from html import escape
import requests
import streamlit as st
from PIL import Image

st.set_page_config(
    page_title="AgroDetect AI — Optical Plant Pathology",
    page_icon="🌿",
    layout="wide",
    initial_sidebar_state="collapsed"
)


def get_backend_url() -> str:
    env_url = os.getenv("BACKEND_URL")
    if env_url:
        return env_url.rstrip("/") + "/predict"

    try:
        secret_url = st.secrets.get("BACKEND_URL")
        if secret_url:
            return str(secret_url).rstrip("/") + "/predict"
    except Exception:
        pass

    return "https://agrodetect-ai-backend.onrender.com/predict"


BACKEND_URL = get_backend_url()

# ================= SINGLE-LINE VECTOR SVG ICONS (ZERO INDENTATION BUGS) =================
SVG_BRAND_LOGO = (
    '<div class="logo-orb">'
    '<svg width="22" height="22" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">'
    '<path d="M17 3C11.5 3 6 7.5 6 14C6 16.8 7.2 19.2 9 20.8C9.2 15.5 12.5 11 18 9C14.5 12 12.5 16 12.5 21C17.8 20.5 21 15.8 21 9.5C21 6.5 19.5 3 17 3Z" stroke="url(#leaf_grad)" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>'
    '<path d="M5 21L9.5 16.5" stroke="#22C55E" stroke-width="2" stroke-linecap="round"/>'
    '<defs><linearGradient id="leaf_grad" x1="6" y1="3" x2="21" y2="21" gradientUnits="userSpaceOnUse">'
    '<stop stop-color="#4ADE80"/><stop offset="1" stop-color="#38BDF8"/>'
    '</linearGradient></defs></svg></div>'
)

SVG_SCANNER = '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#4ADE80" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M3 7V5a2 2 0 0 1 2-2h2"/><path d="M17 3h2a2 2 0 0 1 2 2v2"/><path d="M21 17v2a2 2 0 0 1-2 2h-2"/><path d="M7 21H5a2 2 0 0 1-2-2v-2"/><circle cx="12" cy="12" r="3"/><path d="m16 16-1.9-1.9"/></svg>'

SVG_TELEMETRY = '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#38BDF8" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M22 12h-4l-3 9L9 3l-3 9H2"/></svg>'

SVG_SPARK = '<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="#4ADE80" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 3v18"/><path d="M3 12h18"/><path d="m18.36 5.64-12.72 12.72"/><path d="m5.64 5.64 12.72 12.72"/></svg>'

SVG_SUN = '<svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="#4ADE80" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="4"/><path d="M12 2v2"/><path d="M12 20v2"/><path d="m4.93 4.93 1.41 1.41"/><path d="m17.66 17.66 1.41 1.41"/><path d="M2 12h2"/><path d="M20 12h2"/><path d="m6.34 17.66-1.41 1.41"/><path d="m19.07 4.93-1.41 1.41"/></svg>'

SVG_FOCUS = '<svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="#38BDF8" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><line x1="22" y1="12" x2="18" y2="12"/><line x1="6" y1="12" x2="2" y2="12"/><line x1="12" y1="6" x2="12" y2="2"/><line x1="12" y1="22" x2="12" y2="18"/></svg>'

SVG_CROPS = '<svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="#4ADE80" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M7 20h10"/><path d="M10 20c5.5-2.5.8-6.4 3-10"/><path d="M9.5 9.4c1.1.8 1.8 2.2 2.3 3.7-2 .4-3.5.4-4.8-.3-1.2-.6-2.3-1.9-3-4.2 2.8-.5 4.4 0 5.5.8z"/><path d="M14.1 6a7 7 0 0 0-1.1 4c1.9-.1 3.3-.6 4.3-1.4 1-1 1.6-2.3 1.7-4.6-2.7.1-4 1-4.9 2z"/></svg>'

SVG_DNA = '<svg width="26" height="26" viewBox="0 0 24 24" fill="none" stroke="#38BDF8" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M2 15c6.667-6 13.333 0 20-6"/><path d="M9 22c1.798-1.998 2.518-3.995 2.807-5.993"/><path d="M15 2c-1.798 1.998-2.518 3.995-2.807 5.993"/><path d="m17 6-2.5-2.5"/><path d="m14 8-1-1"/><path d="m7 18 2.5 2.5"/><path d="m3.5 14.5.5.5"/><path d="m20 9 .5.5"/><path d="m6.5 12.5 1 1"/><path d="m16.5 10.5 1 1"/><path d="m10 16 1.5 1.5"/></svg>'


def load_optical_glass_css():
    st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=Inter:wght@300;400;500;600&family=JetBrains+Mono:wght@400;500;600&display=swap');

/* ================= BASE & OPTICAL MATRIX GRID ================= */
.stApp {
    background-color: #060A12;
    background-image:
        radial-gradient(rgba(255, 255, 255, 0.055) 1px, transparent 1px),
        radial-gradient(circle at 15% 10%, rgba(34, 197, 94, 0.12) 0%, transparent 40%),
        radial-gradient(circle at 85% 15%, rgba(56, 189, 248, 0.10) 0%, transparent 40%),
        radial-gradient(circle at 50% 85%, rgba(34, 197, 94, 0.07) 0%, transparent 45%);
    background-size: 28px 28px, 100% 100%, 100% 100%, 100% 100%;
    font-family: 'Inter', sans-serif;
    color: #F8FAFC;
    overflow-x: hidden;
}

.block-container {
    padding-top: 1.5rem !important;
    padding-bottom: 4rem !important;
    max-width: 1180px !important;
}

[data-testid="stHeader"], [data-testid="stToolbar"], #MainMenu, footer, header, .stMarkdown h1 a {
    display: none !important;
}

/* ================= TRUE REFRACTIVE CLEAR GLASS ================= */
.clear-glass {
    position: relative;
    background: linear-gradient(165deg, rgba(255, 255, 255, 0.03) 0%, rgba(255, 255, 255, 0.008) 100%);
    backdrop-filter: blur(20px);
    -webkit-backdrop-filter: blur(20px);
    border-radius: 26px;
    border: 1px solid rgba(255, 255, 255, 0.12);
    box-shadow:
        0 24px 48px -12px rgba(0, 0, 0, 0.65),
        inset 0 1px 0 0 rgba(255, 255, 255, 0.38),
        inset 1px 0 0 0 rgba(255, 255, 255, 0.12),
        inset 0 -1px 0 0 rgba(56, 189, 248, 0.12);
    transition: all 0.28s cubic-bezier(0.16, 1, 0.3, 1);
}

.clear-glass:hover {
    border-color: rgba(255, 255, 255, 0.22);
    box-shadow:
        0 28px 56px -12px rgba(0, 0, 0, 0.75),
        inset 0 1px 0 0 rgba(255, 255, 255, 0.52),
        inset 0 -1px 0 0 rgba(34, 197, 94, 0.24);
}

/* ================= TOP NAVBAR & VECTOR LOGO ================= */
.glass-nav {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 0.65rem 1.4rem;
    border-radius: 999px;
    margin-bottom: 1.75rem;
}

.brand-wrap {
    display: flex;
    align-items: center;
    gap: 0.75rem;
}

.logo-orb {
    width: 38px;
    height: 38px;
    border-radius: 12px;
    background: linear-gradient(135deg, rgba(34, 197, 94, 0.15), rgba(56, 189, 248, 0.12));
    border: 1px solid rgba(255, 255, 255, 0.22);
    box-shadow:
        0 4px 15px rgba(34, 197, 94, 0.2),
        inset 0 1px 0 rgba(255, 255, 255, 0.45);
    display: flex;
    align-items: center;
    justify-content: center;
}

.brand-name {
    font-family: 'Plus Jakarta Sans', sans-serif;
    font-size: 1.2rem;
    font-weight: 800;
    color: #FFFFFF;
    letter-spacing: -0.02em;
}

.brand-tag {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.68rem;
    color: #4ADE80;
    background: rgba(34, 197, 94, 0.1);
    border: 1px solid rgba(34, 197, 94, 0.28);
    padding: 0.15rem 0.5rem;
    border-radius: 6px;
}

.glass-pill {
    display: inline-flex;
    align-items: center;
    gap: 0.4rem;
    background: rgba(255, 255, 255, 0.02);
    backdrop-filter: blur(12px);
    border: 1px solid rgba(255, 255, 255, 0.12);
    box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.28);
    padding: 0.35rem 0.9rem;
    border-radius: 999px;
    font-size: 0.76rem;
    font-weight: 500;
    color: rgba(255, 255, 255, 0.8);
}

.glass-pill b {
    font-family: 'JetBrains Mono', monospace;
    color: #38BDF8;
    font-weight: 600;
}

.status-pill {
    display: inline-flex;
    align-items: center;
    gap: 0.45rem;
    background: rgba(34, 197, 94, 0.06);
    border: 1px solid rgba(34, 197, 94, 0.3);
    box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.25);
    color: #4ADE80;
    font-family: 'JetBrains Mono', monospace;
    font-weight: 600;
    font-size: 0.72rem;
    padding: 0.38rem 0.95rem;
    border-radius: 999px;
    letter-spacing: 0.04em;
}

.pulse-dot {
    width: 7px;
    height: 7px;
    border-radius: 50%;
    background: #4ADE80;
    box-shadow: 0 0 10px #4ADE80;
}

/* ================= HERO STAGE ================= */
.glass-hero {
    padding: 2.8rem 2.2rem 2.4rem 2.2rem;
    text-align: center;
    margin-bottom: 1.5rem;
    border-radius: 30px;
}

.hero-heading {
    font-family: 'Plus Jakarta Sans', sans-serif;
    font-size: 3.15rem;
    font-weight: 800;
    letter-spacing: -0.03em;
    line-height: 1.12;
    margin: 0.85rem 0 0.75rem 0;
    color: #FFFFFF;
}

.hero-heading span {
    background: linear-gradient(92deg, #4ADE80 0%, #22C55E 45%, #38BDF8 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}

/* ================= TRANSPARENT FILE UPLOADER ================= */
[data-testid="stFileUploader"] {
    background: linear-gradient(165deg, rgba(255, 255, 255, 0.025) 0%, rgba(255, 255, 255, 0.006) 100%) !important;
    backdrop-filter: blur(20px) !important;
    -webkit-backdrop-filter: blur(20px) !important;
    border-radius: 26px !important;
    padding: 1rem !important;
    border: 1px solid rgba(255, 255, 255, 0.12) !important;
    box-shadow:
        0 20px 45px rgba(0, 0, 0, 0.5),
        inset 0 1px 0 rgba(255, 255, 255, 0.35) !important;
}

[data-testid="stFileUploaderDropzone"] {
    background: transparent !important;
    border: 1px dashed rgba(255, 255, 255, 0.18) !important;
    border-radius: 18px !important;
    padding: 1.65rem 1.8rem !important;
    transition: all 0.25s ease !important;
}

[data-testid="stFileUploaderDropzone"]:hover {
    background: rgba(34, 197, 94, 0.025) !important;
    border-color: rgba(56, 189, 248, 0.45) !important;
}

[data-testid="stFileUploaderDropzone"] button {
    background: rgba(255, 255, 255, 0.035) !important;
    color: #F8FAFC !important;
    font-family: 'Plus Jakarta Sans', sans-serif !important;
    font-weight: 600 !important;
    font-size: 0.85rem !important;
    border: 1px solid rgba(255, 255, 255, 0.22) !important;
    border-radius: 999px !important;
    padding: 0.45rem 1.35rem !important;
    box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.4), 0 6px 14px rgba(0, 0, 0, 0.3) !important;
}

[data-testid="stFileUploaderDropzone"] button:hover {
    background: rgba(34, 197, 94, 0.12) !important;
    border-color: #4ADE80 !important;
}

[data-testid="stFileUploaderFile"] {
    background: rgba(255, 255, 255, 0.02) !important;
    border: 1px solid rgba(255, 255, 255, 0.1) !important;
    box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.2) !important;
    border-radius: 14px !important;
    padding: 0.4rem 0.9rem !important;
    margin-top: 0.6rem !important;
}

/* ================= OPTICAL HUD VIEWPORT ================= */
.hud-viewport {
    position: relative;
    border-radius: 18px;
    overflow: hidden;
    border: 1px solid rgba(255, 255, 255, 0.14);
    box-shadow: 0 14px 30px rgba(0, 0, 0, 0.5);
    margin-bottom: 1rem;
    background: #04070D;
}

.hud-viewport img {
    width: 100%;
    height: 290px;
    object-fit: cover;
    display: block;
}

.reticle {
    position: absolute;
    width: 18px;
    height: 18px;
    border-color: rgba(74, 222, 128, 0.75);
    border-style: solid;
    pointer-events: none;
}
.r-tl { top: 12px; left: 12px; border-width: 2px 0 0 2px; border-top-left-radius: 4px; }
.r-tr { top: 12px; right: 12px; border-width: 2px 2px 0 0; border-top-right-radius: 4px; }
.r-bl { bottom: 12px; left: 12px; border-width: 0 0 2px 2px; border-bottom-left-radius: 4px; }
.r-br { bottom: 12px; right: 12px; border-width: 0 2px 2px 0; border-bottom-right-radius: 4px; }

/* ================= CTA BUTTON ================= */
.stButton > button {
    background: linear-gradient(135deg, rgba(34, 197, 94, 0.16) 0%, rgba(56, 189, 248, 0.14) 100%) !important;
    backdrop-filter: blur(20px) !important;
    color: #FFFFFF !important;
    font-family: 'Plus Jakarta Sans', sans-serif !important;
    font-weight: 700 !important;
    font-size: 0.92rem !important;
    letter-spacing: 0.06em !important;
    padding: 0.9rem 1.8rem !important;
    border-radius: 999px !important;
    border: 1px solid rgba(74, 222, 128, 0.45) !important;
    box-shadow:
        0 14px 30px rgba(0, 0, 0, 0.45),
        inset 0 1px 0 rgba(255, 255, 255, 0.5) !important;
    transition: all 0.25s ease !important;
}

.stButton > button:hover {
    background: linear-gradient(135deg, rgba(34, 197, 94, 0.26) 0%, rgba(56, 189, 248, 0.24) 100%) !important;
    border-color: #38BDF8 !important;
    transform: translateY(-2px) !important;
    box-shadow:
        0 18px 36px rgba(0, 0, 0, 0.55),
        inset 0 1.5px 0 rgba(255, 255, 255, 0.7),
        0 0 25px rgba(34, 197, 94, 0.22) !important;
}

/* ================= SUB-PANELS & ICON ORBS ================= */
.glass-subpanel {
    background: rgba(255, 255, 255, 0.018);
    border: 1px solid rgba(255, 255, 255, 0.09);
    box-shadow:
        0 8px 20px rgba(0, 0, 0, 0.25),
        inset 0 1px 0 rgba(255, 255, 255, 0.25);
    border-radius: 18px;
    padding: 1.15rem 1.3rem;
    margin-bottom: 0.9rem;
}

.confidence-track {
    width: 100%;
    height: 5px;
    background: rgba(255, 255, 255, 0.07);
    border-radius: 999px;
    overflow: hidden;
    margin-top: 0.65rem;
}

.glass-icon-box {
    width: 46px;
    height: 46px;
    border-radius: 14px;
    background: rgba(255, 255, 255, 0.025);
    border: 1px solid rgba(255, 255, 255, 0.15);
    box-shadow:
        0 8px 18px rgba(0, 0, 0, 0.3),
        inset 0 1px 0 rgba(255, 255, 255, 0.4);
    display: flex;
    align-items: center;
    justify-content: center;
    margin-bottom: 1rem;
}

@media (max-width: 768px) {
    .hero-heading { font-size: 2.2rem; }
}
</style>
""", unsafe_allow_html=True)


def image_to_base64(img: Image.Image) -> str:
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return base64.b64encode(buf.getvalue()).decode()


def render_clear_gauge(pct: float, accent: str) -> str:
    radius = 33
    circ = 2 * 3.14159 * radius
    offset = circ - (pct / 100.0) * circ
    return (
        f'<div style="position:relative;width:82px;height:82px;display:flex;align-items:center;justify-content:center;flex-shrink:0;'
        f'background:rgba(255,255,255,0.02);border-radius:50%;border:1px solid rgba(255,255,255,0.14);'
        f'box-shadow:inset 0 1px 0 rgba(255,255,255,0.32),0 6px 16px rgba(0,0,0,0.35);">'
        f'<svg width="82" height="82" style="transform:rotate(-90deg);">'
        f'<circle cx="41" cy="41" r="{radius}" stroke="rgba(255,255,255,0.08)" stroke-width="6" fill="transparent"/>'
        f'<circle cx="41" cy="41" r="{radius}" stroke="{accent}" stroke-width="6" fill="transparent" '
        f'stroke-dasharray="{circ:.1f}" stroke-dashoffset="{offset:.1f}" stroke-linecap="round"/>'
        f'</svg>'
        f'<div style="position:absolute;font-family:\'JetBrains Mono\',monospace;font-weight:700;font-size:0.9rem;color:#FFFFFF;">'
        f'{pct:.0f}%'
        f'</div></div>'
    )


def main():
    load_optical_glass_css()

    if "result_data" not in st.session_state:
        st.session_state.result_data = None
    if "current_file" not in st.session_state:
        st.session_state.current_file = None

    # ================= NAVBAR =================
    nav_html = (
        f'<div class="clear-glass glass-nav">'
        f'<div class="brand-wrap">'
        f'{SVG_BRAND_LOGO}'
        f'<div class="brand-name">AgroDetect <span style="color:#4ADE80;font-weight:500;">AI</span></div>'
        f'<span class="brand-tag">v2.5</span>'
        f'</div>'
        f'<div style="display:flex;gap:0.6rem;flex-wrap:wrap;">'
        f'<div class="glass-pill">Precision <b>95.4%</b></div>'
        f'<div class="glass-pill">Dataset <b>50K+</b></div>'
        f'<div class="glass-pill">Species <b>20+</b></div>'
        f'</div>'
        f'<div class="status-pill"><span class="pulse-dot"></span>ENGINE READY</div>'
        f'</div>'
    )
    st.markdown(nav_html, unsafe_allow_html=True)

    # ================= HERO =================
    hero_html = (
        f'<div class="clear-glass glass-hero">'
        f'<div class="glass-pill" style="color:#4ADE80;border-color:rgba(34,197,94,0.28);">'
        f'{SVG_SPARK}<span>AI-Powered Plant Pathology Vision</span>'
        f'</div>'
        f'<h1 class="hero-heading">Instant Leaf Disease <span>Diagnostics</span></h1>'
        f'<p style="color:rgba(255,255,255,0.62);font-size:1rem;max-width:560px;margin:0 auto;line-height:1.6;">'
        f'Drop a leaf specimen into the optical glass chamber below for real-time pathogen identification, confidence telemetry, and prescribed remedies.'
        f'</p>'
        f'</div>'
    )
    st.markdown(hero_html, unsafe_allow_html=True)

    # ================= UPLOADER =================
    uploaded_file = st.file_uploader(
        "Upload Leaf Specimen",
        type=["jpg", "jpeg", "png"],
        label_visibility="collapsed"
    )

    if uploaded_file is not None:
        if st.session_state.current_file != uploaded_file.name:
            st.session_state.result_data = None
            st.session_state.current_file = uploaded_file.name

        image = Image.open(uploaded_file)
        b64_img = image_to_base64(image)
        safe_filename = escape(uploaded_file.name[:16])

        st.markdown("<div style='height: 1.15rem;'></div>", unsafe_allow_html=True)
        col_l, col_r = st.columns([1, 1.15], gap="large")

        with col_l:
            st.markdown(
                f'<div class="clear-glass" style="padding:1.6rem;">'
                f'<div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:0.95rem;">'
                f'<div style="display:flex;align-items:center;gap:0.55rem;font-family:\'Plus Jakarta Sans\',sans-serif;font-weight:700;font-size:1rem;">'
                f'{SVG_SCANNER}<span>Specimen Chamber</span>'
                f'</div>'
                f'<span class="status-pill" style="padding:0.2rem 0.7rem;font-size:0.68rem;">LOCKED</span>'
                f'</div>'
                f'<div class="hud-viewport">'
                f'<img src="data:image/png;base64,{b64_img}" alt="Leaf Specimen"/>'
                f'<div class="reticle r-tl"></div>'
                f'<div class="reticle r-tr"></div>'
                f'<div class="reticle r-bl"></div>'
                f'<div class="reticle r-br"></div>'
                f'</div>'
                f'<div style="display:flex;gap:0.5rem;">'
                f'<div class="glass-pill" style="flex:1;justify-content:center;"><b>FILE</b> {safe_filename}</div>'
                f'<div class="glass-pill" style="flex:1;justify-content:center;"><b>SIZE</b> {uploaded_file.size / 1024:.1f}KB</div>'
                f'<div class="glass-pill" style="flex:1;justify-content:center;"><b>RES</b> {image.size[0]}×{image.size[1]}</div>'
                f'</div>'
                f'</div>',
                unsafe_allow_html=True
            )

            st.markdown("<div style='height: 0.75rem;'></div>", unsafe_allow_html=True)
            if st.button("RUN OPTICAL PATHOGEN SCAN", use_container_width=True):
                with st.spinner("Executing neural inference on leaf specimen..."):
                    try:
                        files = {"file": (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type)}
                        response = requests.post(BACKEND_URL, files=files, timeout=60)
                        if response.status_code == 200:
                            st.session_state.result_data = response.json()
                        else:
                            st.error(f"Backend error: {response.status_code}")
                    except Exception as e:
                        st.error(f"Error connecting to backend ({BACKEND_URL}): {str(e)}")

        with col_r:
            res = st.session_state.result_data
            if res is None:
                st.markdown(
                    f'<div class="clear-glass" style="padding:2rem;display:flex;flex-direction:column;align-items:center;justify-content:center;text-align:center;min-height:420px;">'
                    f'<div class="glass-icon-box" style="width:60px;height:60px;margin-bottom:1.1rem;">{SVG_DNA}</div>'
                    f'<h3 style="font-family:\'Plus Jakarta Sans\',sans-serif;font-weight:700;font-size:1.25rem;margin:0 0 0.45rem 0;">Telemetry Standby</h3>'
                    f'<p style="color:rgba(255,255,255,0.58);font-size:0.88rem;max-width:300px;margin:0;line-height:1.55;">'
                    f'Click <b style="color:#4ADE80;">Run Optical Pathogen Scan</b> beneath the specimen chamber to compute disease probability and treatment protocols.'
                    f'</p>'
                    f'</div>',
                    unsafe_allow_html=True
                )
            else:
                conf = float(res.get("confidence", 0))
                if conf > 1.0:
                    conf /= 100.0
                conf = max(0.0, min(conf, 1.0))
                pct = conf * 100

                raw_disease = str(res.get("disease", "Unknown Pathogen")).replace("_", " ")
                disease = escape(raw_disease)
                treatment = escape(str(res.get("treatment", "No treatment information available.")))

                accent = "#4ADE80" if pct >= 80 else "#38BDF8" if pct >= 50 else "#FACC15"
                grade = "High Confidence" if pct >= 80 else "Moderate" if pct >= 50 else "Low Certainty"
                gauge_html = render_clear_gauge(pct, accent)

                report_html = (
                    f'<div class="clear-glass" style="padding:1.65rem;min-height:420px;display:flex;flex-direction:column;justify-content:space-between;">'
                    f'<div>'
                    f'<div style="display:flex;justify-content:space-between;align-items:center;gap:0.75rem;flex-wrap:wrap;margin-bottom:1rem;">'
                    f'<div style="display:flex;align-items:center;gap:0.55rem;font-family:\'Plus Jakarta Sans\',sans-serif;font-weight:700;font-size:1rem;">'
                    f'{SVG_TELEMETRY}<span>Telemetry Report</span>'
                    f'</div>'
                    f'<span class="status-pill" style="color:{accent};border-color:{accent}55;background:rgba(255,255,255,0.02);">● {grade}</span>'
                    f'</div>'
                    f'<div class="glass-subpanel">'
                    f'<div style="display:flex;align-items:center;justify-content:space-between;gap:1rem;">'
                    f'<div style="min-width:0;flex:1;">'
                    f'<div style="font-family:\'JetBrains Mono\',monospace;font-size:0.68rem;text-transform:uppercase;letter-spacing:0.1em;color:rgba(255,255,255,0.48);">Identified Pathogen</div>'
                    f'<div style="font-family:\'Plus Jakarta Sans\',sans-serif;font-size:clamp(1.2rem,2vw,1.5rem);font-weight:800;color:#4ADE80;margin:0.25rem 0;line-height:1.2;overflow-wrap:anywhere;">{disease}</div>'
                    f'<div style="font-size:0.82rem;color:rgba(255,255,255,0.68);">Neural Confidence: <b style="font-family:\'JetBrains Mono\',monospace;color:#38BDF8;">{pct:.1f}%</b></div>'
                    f'</div>'
                    f'{gauge_html}'
                    f'</div>'
                    f'<div class="confidence-track">'
                    f'<div style="width:{pct:.1f}%;height:100%;background:linear-gradient(90deg,#22C55E,#38BDF8);border-radius:999px;"></div>'
                    f'</div>'
                    f'</div>'
                    f'<div class="glass-subpanel">'
                    f'<div style="font-family:\'JetBrains Mono\',monospace;font-size:0.7rem;text-transform:uppercase;letter-spacing:0.09em;color:#38BDF8;font-weight:600;margin-bottom:0.35rem;">Prescribed Treatment Protocol</div>'
                    f'<p style="margin:0;font-size:0.88rem;color:rgba(255,255,255,0.82);line-height:1.55;overflow-wrap:anywhere;">{treatment}</p>'
                    f'</div>'
                    f'</div>'
                    f'<div style="display:flex;gap:0.5rem;flex-wrap:wrap;margin-top:0.3rem;">'
                    f'<span class="glass-pill">Isolate symptomatic leaves</span>'
                    f'<span class="glass-pill">Avoid overhead irrigation</span>'
                    f'<span class="glass-pill">Improve canopy airflow</span>'
                    f'</div>'
                    f'</div>'
                )
                st.markdown(report_html, unsafe_allow_html=True)

    # ================= 3 FEATURE CARDS =================
    st.markdown("<div style='height: 1.75rem;'></div>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3, gap="medium")

    with c1:
        st.markdown(
            f'<div class="clear-glass" style="padding:1.6rem;">'
            f'<div class="glass-icon-box">{SVG_SUN}</div>'
            f'<h4 style="font-family:\'Plus Jakarta Sans\',sans-serif;font-weight:700;font-size:1.04rem;margin:0 0 0.4rem 0;">Diffused Daylight</h4>'
            f'<p style="color:rgba(255,255,255,0.58);font-size:0.86rem;margin:0;line-height:1.55;">Capture specimens in even daylight without harsh direct glares or deep shadows.</p>'
            f'</div>',
            unsafe_allow_html=True
        )

    with c2:
        st.markdown(
            f'<div class="clear-glass" style="padding:1.6rem;">'
            f'<div class="glass-icon-box">{SVG_FOCUS}</div>'
            f'<h4 style="font-family:\'Plus Jakarta Sans\',sans-serif;font-weight:700;font-size:1.04rem;margin:0 0 0.4rem 0;">Macro Focus (6–8 in)</h4>'
            f'<p style="color:rgba(255,255,255,0.58);font-size:0.86rem;margin:0;line-height:1.55;">Hold the lens 6 to 8 inches away so lesion textures remain sharp and clear.</p>'
            f'</div>',
            unsafe_allow_html=True
        )

    with c3:
        st.markdown(
            f'<div class="clear-glass" style="padding:1.6rem;">'
            f'<div class="glass-icon-box">{SVG_CROPS}</div>'
            f'<h4 style="font-family:\'Plus Jakarta Sans\',sans-serif;font-weight:700;font-size:1.04rem;margin:0 0 0.4rem 0;">20+ Crop Varieties</h4>'
            f'<p style="color:rgba(255,255,255,0.58);font-size:0.86rem;margin:0;line-height:1.55;">Optimized across Tomato, Potato, Pepper, Apple, Corn, Rice, and Wheat.</p>'
            f'</div>',
            unsafe_allow_html=True
        )

    st.markdown(
        '<div style="text-align:center;margin-top:2.8rem;color:rgba(255,255,255,0.35);font-size:0.8rem;font-family:\'JetBrains Mono\',monospace;">'
        '© 2026 AGRODETECT AI · OPTICAL PLANT PATHOLOGY ENGINE'
        '</div>',
        unsafe_allow_html=True
    )


if __name__ == "__main__":
    main()