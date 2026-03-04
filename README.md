# 🎨 Holi-fy: The Color Restoration Engine

> **Bring the past to life with AI + Gulaal 🌈**

Holi-fy is a festive, AI-powered web application that transforms old grayscale or faded photographs into vibrant, Holi-inspired masterpieces. Upload any colourless image and watch the colours explode!

---

## ✨ Features

| Feature | Description |
|---------|-------------|
| 🧠 **AI Colorization** | Deep Neural Network (Zhang et al. Caffe model) predicts chrominance from luminance |
| 🎨 **Gulaal Boost** | Post-processing saturation amplification in **L\*a\*b\*** colour space (a\* & b\* channels) |
| 🔀 **Comparison Slider** | Interactive before/after slider powered by `streamlit-image-comparison` |
| 📤 **Drag & Drop Upload** | Supports JPG, PNG, BMP, WEBP up to 10 MB |
| ⬇️ **One-Click Download** | Download the restored image as PNG |
| 📣 **LinkedIn Share** | Pre-written caption with a one-click share button |
| 🎛️ **Adjustable Intensity** | Sidebar slider to control the Gulaal saturation factor |
| 🌑 **Holi Dark Theme** | Glassmorphism UI with animated gradient banner |

---

## 🛠️ Tech Stack

- **Frontend:** Streamlit + custom CSS (glassmorphism, animations)
- **AI Model:** Zhang et al. Caffe Colorization DNN via OpenCV `cv2.dnn`
- **Post-processing:** OpenCV L\*a\*b\* colour space manipulation
- **Image Comparison:** [streamlit-image-comparison](https://pypi.org/project/streamlit-image-comparison/)

---

## 🚀 Run Locally

### Prerequisites

- Python 3.9+ installed
- `pip` available

### Steps

```bash
# 1. Clone the repository
git clone https://github.com/<your-username>/holi-fy.git
cd holi-fy

# 2. Create & activate a virtual environment
python -m venv venv

# Windows
venv\Scripts\activate

# macOS / Linux
source venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Launch the app
streamlit run app.py
```

> **Note:** On first run the app automatically downloads the model weights (~123 MB) into the `models/` directory. Subsequent launches are instant.

---


> The app is optimised for Streamlit Cloud's 1 GB RAM limit. The Caffe model is lightweight (~123 MB) and inference is CPU-friendly.

---

## 📂 Project Structure

```
holi-fy/
├── .streamlit/
│   └── config.toml        # Streamlit theme & server config
├── app.py                  # Main Streamlit application
├── engine.py               # AI colorization engine & Gulaal boost
├── config.py               # Centralised configuration
├── requirements.txt        # Python dependencies
├── .gitignore
└── README.md
```

---

## 🔬 How It Works

```
┌─────────────┐     ┌──────────────┐     ┌─────────────┐     ┌───────────┐
│  Input Image │ ──▶ │  BGR → L*a*b* │ ──▶ │  DNN Predict │ ──▶ │ Gulaal    │
│  (grayscale) │     │  Extract L    │     │  a* & b*     │     │ Boost a*b*│
└─────────────┘     └──────────────┘     └─────────────┘     └───────────┘
                                                                      │
                                                                      ▼
                                                              ┌───────────┐
                                                              │ L*a*b*→BGR│
                                                              │ Vibrant!  │
                                                              └───────────┘
```

1. **L\*a\*b\* Conversion** — The image is converted to CIE L\*a\*b\* colour space so luminance is separated from chrominance.
2. **DNN Inference** — The L (lightness) channel is scaled to 224×224 and fed into the pre-trained Caffe network, which predicts the a\* and b\* chrominance channels.
3. **Gulaal Post-Processing** — The predicted a\* and b\* channels are multiplied by a user-adjustable factor to simulate the vivid, festive look of Gulaal powder.
4. **Reconstruction** — The boosted a\*b\* channels are merged with the original L channel and converted back to BGR/RGB.

---

