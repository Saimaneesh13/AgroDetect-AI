import streamlit as st
import requests
from PIL import Image
import base64
import os
import time

st.set_page_config(
    page_title="AgroDetect AI - Plant Disease Detection",
    page_icon="🌙",
    layout="wide",
    initial_sidebar_state="collapsed"
)

BACKEND_URL = "http://127.0.0.1:8000/predict"


def load_css():
    st.markdown("""
    <style>
/* Import Google Fonts */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700&display=swap');

/* ================= GLOBAL ================= */
.stApp {
    background: 
        radial-gradient(circle at 20% 10%, rgba(34,197,94,0.15), transparent 40%),
        radial-gradient(circle at 80% 0%, rgba(56,189,248,0.12), transparent 40%),
        #0B1220;
    font-family: 'Inter', sans-serif;
}

/* ===== REMOVE TOP EMPTY BAR ===== */

/* Remove Streamlit top padding */
.block-container {
    padding-top: 0rem !important;
    padding-bottom: 0rem !important;
}

/* Hide top header space */
[data-testid="stHeader"] {
    display: none;
}

/* Remove extra top spacing */
[data-testid="stAppViewContainer"] > .main {
    padding-top: 0rem;
}

/* Remove toolbar gap */
[data-testid="stToolbar"] {
    display: none;
}

/* Force remove first element spacing */
section.main > div:first-child {
    padding-top: 0rem !important;
    margin-top: 0rem !important;
}

/* Hide Streamlit Branding */
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}

/* ================= HERO GRADIENT ================= */
.hero-gradient {
    background:
        radial-gradient(circle at 50% -20%, rgba(34,197,94,0.25), transparent 55%),
        radial-gradient(circle at 85% 10%, rgba(56,189,248,0.18), transparent 45%),
        linear-gradient(180deg, #0F172A 0%, #0B1220 100%);
    padding: 2.5rem 0;
    border-radius: 0 0 32px 32px;
    margin-bottom: 1.5rem;
    margin-top: -1rem;  /* pulls it upward for full-bleed premium look */
}

/* ================= MAIN CONTAINER ================= */
.custom-container {
    background: rgba(31, 41, 55, 0.4);
    backdrop-filter: blur(14px);
    -webkit-backdrop-filter: blur(14px);
    border-radius: 28px;
    padding: 2.5rem;
    box-shadow: 0 20px 40px rgba(0, 0, 0, 0.6);
    margin: 1rem 0;
    border: 1px solid rgba(255, 255, 255, 0.06);
}

/* ================= HEADER ================= */
.header-title {
    font-size: 3.8rem;
    font-weight: 700;
    color: #22C55E;
    text-align: center;
    margin-bottom: 0.5rem;
    font-family: 'Plus Jakarta Sans', sans-serif;
    letter-spacing: -0.02em;
    text-shadow:
        0 0 12px rgba(34,197,94,0.45),
        0 0 30px rgba(34,197,94,0.25);
}

.header-subtitle {
    text-align: center;
    color: rgba(255,255,255,0.7);
    font-size: 1.25rem;
    margin-bottom: 2rem;
    font-weight: 400;
    text-shadow: 0 2px 10px rgba(0,0,0,0.5);
}

/* ================= UPLOAD AREA ================= */
.upload-container {
    background: rgba(17, 24, 39, 0.6);
    backdrop-filter: blur(10px);
    -webkit-backdrop-filter: blur(10px);
    border: 2px dashed rgba(34,197,94,0.35);
    border-radius: 22px;
    padding: 2.8rem;
    text-align: center;
    transition: all 0.25s ease;
    margin-bottom: 1rem;
}

.upload-container:hover {
    border-color: #22C55E;
    background: rgba(31,41,55,0.75);
    box-shadow: 0 0 30px rgba(34,197,94,0.25);
}

.drag-area {
    background: rgba(34,197,94,0.1);
    padding: 2rem;
    border-radius: 16px;
    margin: 1rem 0;
    color: white;
    backdrop-filter: blur(5px);
    border: 1px solid rgba(255,255,255,0.05);
}

/* ================= GLASS CARDS ================= */
.feature-card,
.tip-card,
.metric-card,
.result-card {
    background: rgba(31, 41, 55, 0.55);
    backdrop-filter: blur(14px);
    -webkit-backdrop-filter: blur(14px);
    border: 1px solid rgba(255,255,255,0.08);
    box-shadow:
        0 10px 30px rgba(0,0,0,0.5),
        inset 0 1px 0 rgba(255,255,255,0.04);
    transition: all 0.3s cubic-bezier(0.175, 0.885, 0.32, 1.275);
}

.feature-card:hover,
.tip-card:hover,
.metric-card:hover {
    transform: translateY(-6px) scale(1.02);
    border-color: rgba(34,197,94,0.6);
    box-shadow:
        0 20px 40px rgba(0,0,0,0.6),
        inset 0 1px 0 rgba(255,255,255,0.06);
}

/* ================= FEATURE CARD SPECIFIC ================= */
.feature-card {
    border-radius: 20px;
    padding: 1.8rem 1.5rem;
    text-align: center;
    height: 100%;
}

.feature-icon {
    font-size: 2.5rem;
    margin-bottom: 1rem;
    filter: drop-shadow(0 0 8px currentColor);
}

.feature-icon-blue {
    color: #38BDF8;
    text-shadow: 0 0 15px rgba(56,189,248,0.5);
}

.feature-icon-green {
    color: #22C55E;
    text-shadow: 0 0 15px rgba(34,197,94,0.5);
}

.feature-icon-yellow {
    color: #FACC15;
    text-shadow: 0 0 15px rgba(250,204,21,0.5);
}

.feature-title {
    font-weight: 600;
    color: rgba(255,255,255,0.95);
    margin-bottom: 0.5rem;
    font-size: 1.2rem;
}

.feature-description {
    color: rgba(255,255,255,0.6);
    font-size: 0.9rem;
    line-height: 1.5;
}

/* ================= METRIC CARD ================= */
.metric-card {
    border-radius: 16px;
    padding: 1.5rem;
    text-align: center;
}

.metric-value {
    font-size: 1.9rem;
    font-weight: 700;
    color: rgba(255,255,255,0.95);
    margin-bottom: 0.5rem;
}

.metric-label {
    color: rgba(255,255,255,0.5);
    font-size: 0.85rem;
    text-transform: uppercase;
    letter-spacing: 1px;
    font-weight: 500;
}

/* ================= TIP CARD ================= */
.tip-card {
    border-radius: 18px;
    padding: 1.8rem 1.5rem;
    height: 100%;
}

.tip-card h4 {
    color: rgba(255,255,255,0.95);
    margin-bottom: 1rem;
    font-weight: 600;
    font-size: 1.2rem;
}

.tip-card p {
    color: rgba(255,255,255,0.6);
    line-height: 1.6;
    font-size: 0.95rem;
}

/* ================= BUTTON ================= */
.stButton > button {
    background: linear-gradient(135deg, #22C55E, #16A34A);
    color: white;
    border: none;
    padding: 0.9rem 2rem;
    border-radius: 14px;
    font-weight: 600;
    font-size: 1.05rem;
    transition: all 0.25s cubic-bezier(0.175, 0.885, 0.32, 1.275);
    width: 100%;
    box-shadow: 0 10px 25px rgba(34,197,94,0.25);
    border: 1px solid rgba(255,255,255,0.1);
}

.stButton > button:hover {
    transform: translateY(-2px) scale(1.02);
    box-shadow: 0 18px 40px rgba(34,197,94,0.35);
}

/* ================= PROGRESS ================= */
.stProgress > div > div {
    background: linear-gradient(90deg, #22C55E, #38BDF8);
    border-radius: 10px;
}

/* ================= BADGE ================= */
.badge {
    background: rgba(34,197,94,0.15);
    backdrop-filter: blur(10px);
    color: #22C55E;
    padding: 0.6rem 1.8rem;
    border-radius: 50px;
    display: inline-block;
    font-size: 0.9rem;
    font-weight: 600;
    margin-bottom: 1.5rem;
    letter-spacing: 0.5px;
    box-shadow: 0 4px 15px rgba(0, 0, 0, 0.3);
    border: 1px solid rgba(34,197,94,0.3);
}

/* ================= INFO BOX ================= */
.stAlert {
    background: rgba(31, 41, 55, 0.6);
    backdrop-filter: blur(10px);
    border: 1px solid rgba(34,197,94,0.3);
    color: rgba(255,255,255,0.9);
    border-radius: 14px;
}

/* ================= FILE UPLOADER ================= */
.stFileUploader {
    background: rgba(17, 24, 39, 0.6);
    backdrop-filter: blur(10px);
    border: 2px dashed rgba(34,197,94,0.3);
    border-radius: 22px;
    padding: 1rem;
}

.stFileUploader:hover {
    border-color: #22C55E;
    background: rgba(31,41,55,0.75);
}

/* ================= IMAGE INFO CARD ================= */
.image-info-card {
    background: rgba(31, 41, 55, 0.6);
    backdrop-filter: blur(14px);
    border-radius: 18px;
    padding: 1.5rem;
    border: 1px solid rgba(255,255,255,0.08);
    box-shadow: 0 10px 25px rgba(0,0,0,0.5);
}

.image-info-card h4 {
    color: rgba(255,255,255,0.95);
    font-weight: 600;
    margin-bottom: 1rem;
}

.image-info-card p {
    color: rgba(255,255,255,0.6);
}

/* ================= FOOTER ================= */
.footer {
    text-align: center;
    color: rgba(255,255,255,0.5);
    padding: 2rem 0 1rem 0;
    font-size: 0.9rem;
    border-top: 1px solid rgba(255,255,255,0.05);
    margin-top: 2rem;
}

/* ================= SIDEBAR ================= */
.css-1d391kg {
    background: rgba(17, 24, 39, 0.8);
    backdrop-filter: blur(20px);
}

.sidebar-content {
    color: rgba(255,255,255,0.9);
}

/* ================= RESPONSIVE ================= */
@media (max-width: 768px) {
    .header-title {
        font-size: 2.8rem;
    }

    .custom-container {
        padding: 1.5rem;
    }

    .upload-container {
        padding: 1.8rem;
    }
}

/* ================= CUSTOM TEXT COLORS ================= */
h1, h2, h3, h4, h5, h6 {
    color: rgba(255,255,255,0.95) !important;
}

p, li {
    color: rgba(255,255,255,0.7);
}

.stMarkdown {
    color: rgba(255,255,255,0.7);
}

/* ================= SUCCESS MESSAGE ================= */
.stSuccess {
    background: rgba(34,197,94,0.15);
    color: #22C55E;
    border: 1px solid rgba(34,197,94,0.3);
    backdrop-filter: blur(10px);
}

/* ================= ERROR MESSAGE ================= */
.stError {
    background: rgba(239,68,68,0.15);
    color: #ef4444;
    border: 1px solid rgba(239,68,68,0.3);
    backdrop-filter: blur(10px);
}

/* ================= UPLOAD TEXT ================= */
.upload-text {
    color: #22C55E;
    font-weight: 600;
    margin-top: 0.5rem;
    font-size: 1.1rem;
    text-shadow: 0 0 10px rgba(34,197,94,0.3);
}

.limit-text {
    color: rgba(255,255,255,0.4);
    font-size: 0.85rem;
    margin-top: 0.25rem;
}

/* ================= DIVIDER ================= */
.custom-divider {
    height: 1px;
    background: linear-gradient(90deg, transparent, rgba(34,197,94,0.3), rgba(56,189,248,0.3), transparent);
    margin: 2rem 0;
}

/* ================= AI GLOW EFFECT ================= */
.ai-glow {
    position: relative;
}

.ai-glow::after {
    content: '';
    position: absolute;
    top: -2px;
    left: -2px;
    right: -2px;
    bottom: -2px;
    background: linear-gradient(45deg, #22C55E, #38BDF8);
    border-radius: inherit;
    opacity: 0;
    transition: opacity 0.3s;
    z-index: -1;
}

.ai-glow:hover::after {
    opacity: 0.5;
}
</style>
    """, unsafe_allow_html=True)



def get_base64_logo(path):
    try:
        if os.path.exists(path):
            with open(path, "rb") as f:
                return base64.b64encode(f.read()).decode()
    except Exception:
        pass
    return None


def render_sidebar():
    with st.sidebar:
        st.markdown("""
        <div style="text-align:center; padding: 1.5rem 0;">
            <h2 style="color: #22C55E; font-size: 1.8rem; text-shadow: 0 0 15px rgba(34,197,94,0.5);">🌙 AgroDetect AI</h2>
            <div style="height: 2px; background: linear-gradient(90deg, transparent, #22C55E, #38BDF8, transparent); margin: 1rem 0;"></div>
        </div>
        """, unsafe_allow_html=True)

        show_about = st.toggle("📚 About", value=False)

        if show_about:
            st.markdown("""
            <div style="background: rgba(31,41,55,0.6); backdrop-filter: blur(14px); padding: 1.5rem; border-radius: 18px; border: 1px solid rgba(255,255,255,0.08);">
                <h3 style="color: #22C55E;">🤖 About AgroDetect</h3>
                <p style="color: rgba(255,255,255,0.7);">Advanced deep learning system for instant plant disease identification from leaf images.</p>

                <h4 style="color: rgba(255,255,255,0.95); margin-top: 1.2rem;">✨ Key Features</h4>
                <ul style="color: rgba(255,255,255,0.7);">
                    <li><span style="color: #22C55E;">⚡</span> Instant Detection in seconds</li>
                    <li><span style="color: #38BDF8;">🎯</span> 95%+ accuracy on common diseases</li>
                    <li><span style="color: #22C55E;">💊</span> Actionable treatment advice</li>
                    <li><span style="color: #38BDF8;">🌾</span> Support for 20+ crops</li>
                </ul>

                <h4 style="color: rgba(255,255,255,0.95); margin-top: 1.2rem;">🎯 Supported Crops</h4>
                <p style="color: rgba(255,255,255,0.7);">Tomato · Potato · Pepper · Apple · Corn · Rice · Wheat</p>

                <h4 style="color: rgba(255,255,255,0.95); margin-top: 1.2rem;">📊 How It Works</h4>
                <ol style="color: rgba(255,255,255,0.7);">
                    <li>Upload a clear leaf image</li>
                    <li>AI analyzes the image</li>
                    <li>Get disease identification</li>
                    <li>Receive treatment suggestions</li>
                </ol>

                <div style="background: rgba(17,24,39,0.6); padding: 1rem; border-radius: 14px; margin-top: 1.2rem; border: 1px solid rgba(255,255,255,0.05);">
                    <h4 style="color: #22C55E;">📞 Contact</h4>
                    <p style="color: rgba(255,255,255,0.7);">📧 support@agrodetect.ai<br>🌐 www.agrodetect.ai</p>
                </div>

                <p style="text-align:center; color: rgba(255,255,255,0.4); font-size:0.8rem; margin-top: 1rem;">
                    Made with 🌙 for farmers worldwide
                </p>
            </div>
            """, unsafe_allow_html=True)


# MAIN APP

def main():
    # Load CSS
    load_css()

    # Render sidebar
    render_sidebar()

    # Hero Section with Gradient and Glow
    st.markdown('<div class="hero-gradient">', unsafe_allow_html=True)

    # Header Section
    st.markdown("""
    <div style="text-align:center; padding: 2rem 0 1rem 0;">
        <span class="badge">🌿 AI-Powered Plant Health Analysis</span>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<h1 class="header-title">🌙 AgroDetect AI</h1>', unsafe_allow_html=True)
    st.markdown('<p class="header-subtitle">Instant Plant Disease Detection & Treatment Recommendations</p>',
                unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)

    # Feature Cards
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.markdown("""
        <div class="feature-card">
            <div class="feature-icon feature-icon-green">🔍</div>
            <div class="feature-title">Instant Detection</div>
            <div class="feature-description">Get results in seconds</div>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown("""
        <div class="feature-card">
            <div class="feature-icon feature-icon-blue">🎯</div>
            <div class="feature-title">95% Accuracy</div>
            <div class="feature-description">Trained on 50K+ images</div>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown("""
        <div class="feature-card">
            <div class="feature-icon feature-icon-green">💊</div>
            <div class="feature-title">Treatment Advice</div>
            <div class="feature-description">Actionable recommendations</div>
        </div>
        """, unsafe_allow_html=True)

    with col4:
        st.markdown("""
        <div class="feature-card">
            <div class="feature-icon feature-icon-blue">🌾</div>
            <div class="feature-title">Multiple Crops</div>
            <div class="feature-description">Support for 20+ crops</div>
        </div>
        """, unsafe_allow_html=True)

    # Main Container
    st.markdown('<div class="custom-container">', unsafe_allow_html=True)

    # Upload Section
    st.markdown("""
    <h3 style="color: rgba(255,255,255,0.95); margin-bottom: 1rem;">📸 Upload Plant Leaf Image</h3>
    <p style="color: rgba(255,255,255,0.6); margin-bottom: 2rem;">Take a clear photo of the affected leaf for best results</p>
    """, unsafe_allow_html=True)

    # Custom Upload Area with Glass Effect
    st.markdown("""
    <div class="upload-container">
        <div style="font-size: 3.5rem; margin-bottom: 1rem; filter: drop-shadow(0 0 20px rgba(34,197,94,0.5));">📤</div>
        <div class="upload-text">Drag and drop file here</div>
        <div class="limit-text">Limit 200MB per file · JPG, JPEG, PNG</div>
    </div>
    """, unsafe_allow_html=True)

    uploaded_file = st.file_uploader(
        "",
        type=["jpg", "jpeg", "png"],
        label_visibility="collapsed"
    )

    if uploaded_file is not None:
        # Display uploaded image
        col_img, col_info = st.columns([1, 1])

        with col_img:
            image = Image.open(uploaded_file)
            st.image(image, use_container_width=True, caption="Uploaded Leaf Image")

        with col_info:
            st.markdown('<div class="image-info-card">', unsafe_allow_html=True)
            st.markdown("""
            <h4 style="color: rgba(255,255,255,0.95); margin-bottom: 1rem;">📋 Image Information</h4>
            """, unsafe_allow_html=True)

            file_details = {
                "Filename": uploaded_file.name,
                "File Size": f"{uploaded_file.size / 1024:.2f} KB",
                "Image Size": f"{image.size[0]} x {image.size[1]} px"
            }

            for key, value in file_details.items():
                st.markdown(f"**{key}:** {value}")

            st.markdown("</div>", unsafe_allow_html=True)

            # Analyze button
            if st.button("🔬 ANALYZE DISEASE", use_container_width=True):
                with st.spinner("🔄 Analyzing image... This may take a few seconds"):
                    try:
                        files = {
                            "file": (
                                uploaded_file.name,
                                uploaded_file.getvalue(),
                                uploaded_file.type,
                            )
                        }

                        response = requests.post(
                            BACKEND_URL,
                            files=files,
                            timeout=60,
                        )

                        if response.status_code != 200:
                            st.error(f"❌ Backend error ({response.status_code})")
                            st.stop()

                        result = response.json()

                        # Process confidence
                        confidence_raw = result.get("confidence", 0)

                        try:
                            confidence = float(confidence_raw)
                            if confidence > 1:
                                confidence = confidence / 100.0
                            confidence = max(0.0, min(confidence, 1.0))
                        except (ValueError, TypeError):
                            confidence = 0.0

                        # Results Section
                        st.markdown('<div class="result-card">', unsafe_allow_html=True)

                        st.markdown("""
                        <h3 style="color: rgba(255,255,255,0.95); margin-bottom: 1.5rem;">✅ Analysis Results</h3>
                        """, unsafe_allow_html=True)

                        # Metrics
                        col_r1, col_r2, col_r3 = st.columns(3)

                        with col_r1:
                            st.markdown('<div class="metric-card">', unsafe_allow_html=True)
                            st.markdown(f'<div class="metric-value">{result.get("disease", "Unknown")}</div>',
                                        unsafe_allow_html=True)
                            st.markdown('<div class="metric-label">Detected Disease</div>', unsafe_allow_html=True)
                            st.markdown('</div>', unsafe_allow_html=True)

                        with col_r2:
                            st.markdown('<div class="metric-card">', unsafe_allow_html=True)
                            st.progress(confidence)
                            st.markdown(f'<div class="metric-value">{confidence * 100:.1f}%</div>',
                                        unsafe_allow_html=True)
                            st.markdown('<div class="metric-label">Confidence Score</div>', unsafe_allow_html=True)
                            st.markdown('</div>', unsafe_allow_html=True)

                        with col_r3:
                            st.markdown('<div class="metric-card">', unsafe_allow_html=True)
                            severity_icon = "🔴" if confidence > 0.8 else "🟡" if confidence > 0.5 else "🟢"
                            severity = "High" if confidence > 0.8 else "Medium" if confidence > 0.5 else "Low"
                            st.markdown(f'<div class="metric-value">{severity_icon} {severity}</div>',
                                        unsafe_allow_html=True)
                            st.markdown('<div class="metric-label">Severity Level</div>', unsafe_allow_html=True)
                            st.markdown('</div>', unsafe_allow_html=True)

                        # Treatment Section
                        st.markdown("""
                        <h4 style="color: rgba(255,255,255,0.95); margin: 2rem 0 1rem 0;">💊 Recommended Treatment</h4>
                        """, unsafe_allow_html=True)

                        st.info(result.get("treatment", "No treatment information available"))

                        # Additional Tips
                        st.markdown("""
                        <h4 style="color: rgba(255,255,255,0.95); margin: 2rem 0 1rem 0;">📝 Prevention Tips</h4>
                        """, unsafe_allow_html=True)

                        tips = [
                            "🌱 Monitor plants regularly for early signs",
                            "📏 Ensure proper spacing between plants",
                            "💧 Maintain optimal humidity levels",
                            "🛡️ Use disease-resistant varieties",
                            "🔄 Practice crop rotation"
                        ]

                        for tip in tips:
                            st.markdown(f"✅ {tip}")

                        st.markdown('</div>', unsafe_allow_html=True)

                    except requests.exceptions.ConnectionError:
                        st.error("❌ Cannot connect to backend. Please ensure the FastAPI server is running.")
                    except Exception as e:
                        st.error(f"❌ Error: {str(e)}")

    st.markdown('</div>', unsafe_allow_html=True)

    # Divider
    st.markdown('<div class="custom-divider"></div>', unsafe_allow_html=True)

    # Tips Section
    st.markdown('<div class="custom-container">', unsafe_allow_html=True)
    st.markdown("""
    <h3 style="color: rgba(255,255,255,0.95); margin-bottom: 1.5rem;">📸 Tips for Best Results</h3>
    """, unsafe_allow_html=True)

    col_tip1, col_tip2, col_tip3 = st.columns(3)

    with col_tip1:
        st.markdown("""
        <div class="tip-card">
            <div style="font-size: 2.5rem; margin-bottom: 1rem; color: #FACC15; text-shadow: 0 0 15px rgba(250,204,21,0.5);">☀️</div>
            <h4>Good Lighting</h4>
            <p>Ensure the leaf is well-lit and avoid shadows for accurate detection.</p>
        </div>
        """, unsafe_allow_html=True)

    with col_tip2:
        st.markdown("""
        <div class="tip-card">
            <div style="font-size: 2.5rem; margin-bottom: 1rem; color: #38BDF8; text-shadow: 0 0 15px rgba(56,189,248,0.5);">📏</div>
            <h4>Clear Focus</h4>
            <p>Take the photo from 6-8 inches away with the leaf in sharp focus.</p>
        </div>
        """, unsafe_allow_html=True)

    with col_tip3:
        st.markdown("""
        <div class="tip-card">
            <div style="font-size: 2.5rem; margin-bottom: 1rem; color: #22C55E; text-shadow: 0 0 15px rgba(34,197,94,0.5);">🎯</div>
            <h4>Single Leaf</h4>
            <p>Focus on one affected leaf at a time for best results.</p>
        </div>
        """, unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)

    # Footer
    st.markdown("""
    <div class="footer">
        <p>© 2025 AgroDetect AI - Intelligent Plant Disease Detection</p>
        <p style="font-size: 0.85rem; color: #22C55E; text-shadow: 0 0 10px rgba(34,197,94,0.3);">Making farming smarter, one leaf at a time 🌙</p>
    </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()