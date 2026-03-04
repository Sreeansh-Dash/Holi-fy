"""
🎨 Holi-fy: The Color Restoration Engine
==========================================
A festive, AI-powered app that breathes vibrant, Holi-inspired
colours into old grayscale or faded photographs.

Run locally:
    streamlit run app.py
"""

from __future__ import annotations

import io
import random
import time
from pathlib import Path

import streamlit as st
from PIL import Image
from streamlit_image_comparison import image_comparison

import config
from engine import download_model_assets, load_colorization_model, restore_colors

# ─── Festive Spinner Messages ───────────────────────────────────────────────
FESTIVE_MESSAGES = [
    "🎨 Throwing Gulaal on your memory …",
    "🌈 Mixing colours for you …",
    "✨ Almost there — adding the final splash of colour …",
    "💜 Painting the magic — hang tight …",
    "🎉 Sprinkling Holi vibes …",
]

# ─── Page Configuration ─────────────────────────────────────────────────────
st.set_page_config(
    page_title="Holi-fy • Bring Old Photos to Life",
    page_icon="🎨",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ─── Custom CSS ──────────────────────────────────────────────────────────────
st.markdown(
    """
    <style>
    /* ── Import Google Font ───────────────────────────────────────── */
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700;800;900&display=swap');

    /* ── Global overrides ─────────────────────────────────────────── */
    html, body, [class*="st-"] {
        font-family: 'Outfit', sans-serif;
    }
    .stApp {
        background: linear-gradient(160deg, #0E0B16 0%, #1A1130 50%, #0E0B16 100%);
    }

    /* ── Hero Banner ──────────────────────────────────────────────── */
    .hero-banner {
        text-align: center;
        padding: 2rem 1.5rem 0.8rem;
        position: relative;
    }
    .hero-banner h1 {
        font-weight: 900;
        font-size: 3.4rem;
        letter-spacing: -1px;
        background: linear-gradient(135deg, #FF00FF, #FFD700, #00E5FF, #FF4081, #76FF03, #AA00FF);
        background-size: 400% 400%;
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        animation: gradientShift 6s ease infinite;
        margin-bottom: 0.3rem;
    }
    @keyframes gradientShift {
        0%   { background-position: 0% 50%; }
        50%  { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }
    .hero-banner .tagline {
        color: #c4b5fd;
        font-size: 1.15rem;
        font-weight: 400;
        margin-top: 0;
        line-height: 1.6;
    }

    /* ── Colour Burst Dots ────────────────────────────────────────── */
    .color-dots {
        display: flex;
        justify-content: center;
        gap: 10px;
        margin: 0.8rem 0 0.4rem;
    }
    .color-dots span {
        width: 14px;
        height: 14px;
        border-radius: 50%;
        display: inline-block;
        animation: pop 1.4s ease-in-out infinite;
    }
    .color-dots span:nth-child(1) { background: #FF00FF; animation-delay: 0s; }
    .color-dots span:nth-child(2) { background: #FFD700; animation-delay: 0.15s; }
    .color-dots span:nth-child(3) { background: #00E5FF; animation-delay: 0.3s; }
    .color-dots span:nth-child(4) { background: #FF4081; animation-delay: 0.45s; }
    .color-dots span:nth-child(5) { background: #76FF03; animation-delay: 0.6s; }
    .color-dots span:nth-child(6) { background: #AA00FF; animation-delay: 0.75s; }
    @keyframes pop {
        0%, 100% { transform: scale(1); opacity: 0.8; }
        50%      { transform: scale(1.5); opacity: 1; }
    }

    /* ── 3-Step Icon Bar ──────────────────────────────────────────── */
    .steps-bar {
        display: flex;
        justify-content: center;
        align-items: center;
        gap: 0;
        margin: 1.2rem auto 1.5rem;
        max-width: 650px;
    }
    .step-bubble {
        text-align: center;
        flex: 1;
    }
    .step-bubble .step-emoji {
        font-size: 2rem;
        display: block;
        margin-bottom: 0.3rem;
    }
    .step-bubble .step-label {
        font-size: 0.85rem;
        font-weight: 600;
        color: #c4b5fd;
    }
    .step-arrow {
        font-size: 1.4rem;
        color: rgba(255, 255, 255, 0.2);
        padding: 0 0.3rem;
        margin-top: -1.2rem;
    }

    /* ── Glass Card ───────────────────────────────────────────────── */
    .glass-card {
        background: rgba(26, 22, 37, 0.65);
        backdrop-filter: blur(14px);
        -webkit-backdrop-filter: blur(14px);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 16px;
        padding: 2rem;
        margin: 1rem 0;
    }

    /* ── Upload Area ──────────────────────────────────────────────── */
    [data-testid="stFileUploader"] {
        border: 2px dashed rgba(170, 0, 255, 0.4) !important;
        border-radius: 14px !important;
        padding: 1.5rem !important;
        transition: border-color 0.3s;
    }
    [data-testid="stFileUploader"]:hover {
        border-color: #FF00FF !important;
    }

    /* ── Buttons ───────────────────────────────────────────────────── */
    .stDownloadButton > button,
    .stButton > button {
        background: linear-gradient(135deg, #AA00FF 0%, #FF00FF 100%);
        color: white !important;
        border: none;
        border-radius: 12px;
        font-weight: 700;
        font-family: 'Outfit', sans-serif;
        font-size: 1.05rem;
        padding: 0.75rem 2rem;
        transition: transform 0.15s, box-shadow 0.25s;
    }
    .stDownloadButton > button:hover,
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 30px rgba(170, 0, 255, 0.5);
    }

    /* ── Feature Pills ────────────────────────────────────────────── */
    .feature-pill {
        display: inline-block;
        background: rgba(170, 0, 255, 0.12);
        color: #d8b4fe;
        border: 1px solid rgba(170, 0, 255, 0.25);
        border-radius: 20px;
        padding: 0.4rem 1rem;
        font-size: 0.88rem;
        font-weight: 500;
        margin: 0.25rem;
    }

    /* ── Hide Streamlit Branding ───────────────────────────────────── */
    #MainMenu { visibility: hidden; }
    footer { visibility: hidden; }
    header { visibility: hidden; }

    /* ── Hide sidebar toggle (no sidebar at all) ─────────────────── */
    [data-testid="collapsedControl"] { display: none; }

    /* ── Results section ──────────────────────────────────────────── */
    .results-header {
        text-align: center;
        margin: 1.5rem 0 0.8rem;
    }
    .results-header h2 {
        background: linear-gradient(90deg, #FF00FF, #FFD700, #00E5FF);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 800;
    }

    /* ── Tip box ──────────────────────────────────────────────────── */
    .tip-box {
        background: rgba(255, 215, 0, 0.06);
        border: 1px solid rgba(255, 215, 0, 0.2);
        border-radius: 12px;
        padding: 1rem 1.4rem;
        margin: 1rem 0;
        color: #fde68a;
        font-size: 0.92rem;
    }

    /* ── Stats Row ────────────────────────────────────────────────── */
    .stats-row {
        display: flex;
        justify-content: center;
        gap: 2.5rem;
        margin: 1.5rem 0;
        flex-wrap: wrap;
    }
    .stat-item { text-align: center; }
    .stat-item .stat-value {
        font-size: 1.6rem;
        font-weight: 800;
        background: linear-gradient(135deg, #FF00FF, #FFD700);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    .stat-item .stat-label {
        color: #94a3b8;
        font-size: 0.85rem;
        font-weight: 400;
    }

    /* ── Footer ───────────────────────────────────────────────────── */
    .app-footer {
        text-align: center;
        padding: 2rem 0 1rem;
        border-top: 1px solid rgba(255, 255, 255, 0.06);
        margin-top: 2rem;
    }
    .app-footer p {
        color: #64748b;
        font-size: 0.85rem;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# ─── Model Caching ──────────────────────────────────────────────────────────
@st.cache_resource(show_spinner=False)
def get_model():
    """Download assets and load the model exactly once."""
    paths = download_model_assets()
    return load_colorization_model(paths)


# ─── Helper: Validate Upload ────────────────────────────────────────────────
def validate_upload(uploaded_file) -> tuple[bool, str]:
    """Validate file type and size. Returns (ok, message)."""
    ext = Path(uploaded_file.name).suffix.lstrip(".").lower()
    if ext not in config.ALLOWED_EXTENSIONS:
        return False, (
            f"❌ **Unsupported format** `.{ext}`. "
            f"Please upload one of: {', '.join(config.ALLOWED_EXTENSIONS)}"
        )
    if uploaded_file.size > config.MAX_FILE_SIZE_BYTES:
        return False, (
            f"❌ **File too large** ({uploaded_file.size / 1024 / 1024:.1f} MB). "
            f"Max allowed: {config.MAX_FILE_SIZE_MB} MB."
        )
    return True, ""


# ═════════════════════════════════════════════════════════════════════════════
#  HERO SECTION
# ═════════════════════════════════════════════════════════════════════════════
st.markdown(
    """
    <div class="hero-banner">
        <div class="color-dots">
            <span></span><span></span><span></span>
            <span></span><span></span><span></span>
        </div>
        <h1>Holi-fy</h1>
        <p class="tagline">
            Turn your old black &amp; white photos into vibrant, colourful memories — powered by AI ✨
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)

# ── 3-Step Icon Bar ─────────────────────────────────────────────────────────
st.markdown(
    """
    <div class="steps-bar">
        <div class="step-bubble">
            <span class="step-emoji">📤</span>
            <span class="step-label">Upload</span>
        </div>
        <div class="step-arrow">→</div>
        <div class="step-bubble">
            <span class="step-emoji">🤖</span>
            <span class="step-label">AI Process</span>
        </div>
        <div class="step-arrow">→</div>
        <div class="step-bubble">
            <span class="step-emoji">🎉</span>
            <span class="step-label">Celebrate</span>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

# Feature pills
st.markdown(
    """
    <div style="text-align:center; margin-bottom:1.5rem;">
        <span class="feature-pill">✨ AI-Powered</span>
        <span class="feature-pill">⚡ Instant Results</span>
        <span class="feature-pill">📥 Free Download</span>
        <span class="feature-pill">🔒 No Sign-up</span>
    </div>
    """,
    unsafe_allow_html=True,
)


# ═════════════════════════════════════════════════════════════════════════════
#  CENTRED CONTENT WRAPPER
# ═════════════════════════════════════════════════════════════════════════════
_pad_l, centre, _pad_r = st.columns([1, 6, 1])

with centre:

    # ─── FILE UPLOADER ───────────────────────────────────────────────────
    st.markdown("---")
    st.markdown("### 📤 Upload Your Photo")
    st.caption("Drag & drop or click to browse • JPG, PNG, BMP, WEBP • Up to 10 MB")
    uploaded = st.file_uploader(
        "Drag & drop or browse",
        type=config.ALLOWED_EXTENSIONS,
        label_visibility="collapsed",
    )

    # ─── PROCESSING FLOW ────────────────────────────────────────────────
    if uploaded is not None:
        # Validate
        ok, msg = validate_upload(uploaded)
        if not ok:
            st.error(msg)
            st.stop()

        # Show preview
        original_pil = Image.open(uploaded).convert("RGB")
        st.image(original_pil, caption="Your uploaded photo", use_container_width=True)

        # Magic Colorize button
        st.markdown("")
        btn_col1, btn_col2, btn_col3 = st.columns([1, 2, 1])
        with btn_col2:
            colorize_clicked = st.button(
                "🎨 Magic Colorize!",
                use_container_width=True,
                type="primary",
            )

        if colorize_clicked:
            # Store result in session state so it persists after rerun
            # Load model
            with st.spinner(random.choice(FESTIVE_MESSAGES)):
                net = get_model()

            # Run colorization with festive spinner
            with st.spinner(random.choice(FESTIVE_MESSAGES)):
                restored_pil = restore_colors(
                    net, original_pil,
                    saturation_boost=config.DEFAULT_SATURATION_BOOST,
                )

            st.session_state["result_original"] = original_pil
            st.session_state["result_colorized"] = restored_pil

        # ── Show Results (persisted in session state) ────────────────────
        if "result_colorized" in st.session_state and uploaded is not None:
            original_display = st.session_state["result_original"]
            restored_display = st.session_state["result_colorized"]

            st.markdown("---")
            st.markdown(
                """
                <div class="results-header">
                    <h2>✨ Your Holi Transformation ✨</h2>
                </div>
                """,
                unsafe_allow_html=True,
            )

            # Full-width comparison slider (primary output)
            image_comparison(
                img1=original_display,
                img2=restored_display,
                label1="⬅ Before",
                label2="After ➡",
                width=700,
                starting_position=50,
                show_labels=True,
                make_responsive=True,
            )

            st.markdown(
                """
                <div class="tip-box" style="text-align: center; margin-top: 1rem;">
                    👆 Drag the slider left and right to compare before &amp; after
                </div>
                """,
                unsafe_allow_html=True,
            )

            # Side-by-side detail
            st.markdown("")
            col1, col2 = st.columns(2)
            with col1:
                st.markdown(
                    '<p style="text-align:center; color:#94a3b8; font-weight:600;">Original</p>',
                    unsafe_allow_html=True,
                )
                st.image(original_display, use_container_width=True)
            with col2:
                st.markdown(
                    '<p style="text-align:center; color:#c084fc; font-weight:600;">Holi-fied 🎨</p>',
                    unsafe_allow_html=True,
                )
                st.image(restored_display, use_container_width=True)

            # Download button
            st.markdown("")
            dl_col1, dl_col2, dl_col3 = st.columns([1, 2, 1])
            with dl_col2:
                buf = io.BytesIO()
                restored_display.save(buf, format="PNG")
                st.download_button(
                    label="⬇️  Download Your Colourful Photo",
                    data=buf.getvalue(),
                    file_name="holifyed_image.png",
                    mime="image/png",
                    use_container_width=True,
                )

    else:
        # ── Empty State ──────────────────────────────────────────────────
        # Clear any stale results
        st.session_state.pop("result_original", None)
        st.session_state.pop("result_colorized", None)

        st.markdown(
            """
            <div class="glass-card" style="text-align:center; padding:3rem;">
                <p style="font-size:3.5rem; margin:0;">📸</p>
                <p style="color:#e2d9f3; font-size:1.15rem; font-weight:600; margin-top:1rem;">
                    Your colourful memories are waiting
                </p>
                <p style="color:#94a3b8; font-size:0.95rem; margin-top:0.4rem;">
                    Upload a grayscale or faded photo above and watch the transformation ✨
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )

        # Mini stats
        st.markdown(
            """
            <div class="stats-row">
                <div class="stat-item">
                    <div class="stat-value">&lt; 10s</div>
                    <div class="stat-label">Processing Time</div>
                </div>
                <div class="stat-item">
                    <div class="stat-value">5+</div>
                    <div class="stat-label">Formats Supported</div>
                </div>
                <div class="stat-item">
                    <div class="stat-value">100%</div>
                    <div class="stat-label">Free to Use</div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )


# ═════════════════════════════════════════════════════════════════════════════
#  FOOTER
# ═════════════════════════════════════════════════════════════════════════════
st.markdown(
    """
    <div class="app-footer">
        <p>
            Made with ❤️ for <strong style="color:#c084fc;">Holi 2026</strong>
            &nbsp;•&nbsp; Powered by AI
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)
