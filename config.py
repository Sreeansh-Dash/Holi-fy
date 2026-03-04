"""
Holi-fy Configuration Module
=============================
Centralized configuration for the Holi-fy Color Restoration Engine.
"""

# ─── File Upload Constraints ────────────────────────────────────────────────
ALLOWED_EXTENSIONS = ["jpg", "jpeg", "png", "bmp", "webp"]
MAX_FILE_SIZE_MB = 10
MAX_FILE_SIZE_BYTES = MAX_FILE_SIZE_MB * 1024 * 1024

# ─── Image Processing ───────────────────────────────────────────────────────
# Maximum dimension (width or height) for processing. Larger images are
# scaled down to this size to keep inference fast.
MAX_PROCESSING_DIM = 800

# ─── Gulaal Saturation Boost ────────────────────────────────────────────────
# Scale factor applied to the a* and b* channels in L*a*b* colour space.
# 1.0 = no change, 1.5 = 50 % more vivid, 2.0 = double saturation.
DEFAULT_SATURATION_BOOST = 1.6
MIN_SATURATION_BOOST = 1.0
MAX_SATURATION_BOOST = 2.5
SATURATION_STEP = 0.1

# ─── Model Paths (Caffe Colorization) ───────────────────────────────────────
MODEL_DIR = "models"
PROTOTXT_FILE = "colorization_deploy_v2.prototxt"
CAFFEMODEL_FILE = "colorization_release_v2.caffemodel"
HULL_PTS_FILE = "pts_in_hull.npy"

# URLs for auto-download
PROTOTXT_URL = (
    "https://raw.githubusercontent.com/richzhang/colorization/"
    "caffe/colorization/models/colorization_deploy_v2.prototxt"
)
CAFFEMODEL_URL = (
    "https://www.dropbox.com/s/dx0qvhhp5hbcx7z/"
    "colorization_release_v2.caffemodel?dl=1"
)

# Minimum expected size for the caffemodel (actual ~123 MB).
# If smaller, the download is corrupt (e.g. an HTML error page).
CAFFEMODEL_MIN_BYTES = 100 * 1024 * 1024  # 100 MB
HULL_PTS_URL = (
    "https://raw.githubusercontent.com/richzhang/colorization/"
    "caffe/colorization/resources/pts_in_hull.npy"
)

# ─── UI Theme Colours (Holi Palette) ────────────────────────────────────────
HOLI_COLORS = {
    "magenta":  "#FF00FF",
    "yellow":   "#FFD700",
    "cyan":     "#00E5FF",
    "orange":   "#FF6F00",
    "pink":     "#FF4081",
    "green":    "#76FF03",
    "purple":   "#AA00FF",
    "bg_dark":  "#0E0B16",
    "bg_card":  "#1A1625",
    "text":     "#F5F5F5",
}

# ─── LinkedIn Share ─────────────────────────────────────────────────────────
LINKEDIN_CAPTION = (
    "🎨 Just built Holi-fy — a Color Restoration Engine that brings "
    "old grayscale photos back to life with AI!\\n\\n"
    "🔬 Tech Stack:\\n"
    "• Deep Neural Network (Caffe) for automatic colorization\\n"
    "• OpenCV L*a*b* post-processing for a vibrant 'Gulaal' saturation boost\\n"
    "• Streamlit for interactive before/after comparison\\n\\n"
    "Upload any faded or grayscale photo and watch the colours explode. "
    "Happy Holi! 🌈\\n\\n"
    "#Holi #AI #MachineLearning #ComputerVision #OpenCV #Streamlit "
    "#DeepLearning #ImageColorization #Python"
)
