# 🌐 OmniSave - Universal Media & Audio Downloader

A modern, fast web application to download **Reels, Shorts, Videos, and Audio (MP3)** from **Instagram, YouTube, and Facebook**.

Designed with a SaaS aesthetic: default sleek **Dark Mode**, with a one-click toggle to a crisp **Light Mode with high-contrast dark buttons**.

---

## 🚀 Key Capabilities

- **📸 Instagram Support**:
  - Download Instagram Reels and Videos in highest quality MP4.
  - Extract original reel songs and background audio directly to 192kbps MP3.
- **▶️ YouTube Support**:
  - Download YouTube Shorts and standard YouTube videos up to 1080p Full HD MP4.
  - Extract audio tracks and music to crisp 192kbps MP3.
- **📘 Facebook Support**:
  - Download Facebook Watch clips, reels, and video posts to MP4 or MP3.
- **⚡ Automatic Platform Detection**:
  - Real-time link parsing detects whether the pasted URL is from Instagram, YouTube, or Facebook.
- **🌓 Dark & Light Theme Switcher**:
  - **Default Dark Mode**: Deep slate aesthetic (`#09090b`) with refined borders.
  - **Light Mode**: Crisp white layout with bold dark buttons (`#09090b`).
  - Saved in browser `localStorage` across visits.
- **👁️ In-Browser Preview**:
  - Play videos and listen to audio tracks in the browser before saving.
- **📋 One-Click Clipboard Paste**:
  - Dedicated Paste button reads directly from the clipboard.
- **🧹 Automatic Temporary Storage Cleanup**:
  - Automatically cleans files older than 30 minutes to preserve disk space.

---

## 🛠️ Tech Stack

| Component | Technology | Purpose |
| :--- | :--- | :--- |
| **Backend** | Python 3.10+, Flask | Fast REST API & media controller |
| **Media Engine** | `yt-dlp` | Universal stream resolution for Instagram, YouTube, & Facebook |
| **Audio Processing** | `imageio-ffmpeg` / FFmpeg | Seamless MP3 encoding without manual system installation |
| **Frontend** | HTML5, CSS3, JavaScript | Modern SaaS UI, theme toggle, and responsive components |

---

## 📁 Project Directory

```text
C:\Users\devd1\Downloads\Projects\insta download\
├── app.py                     # Flask backend & REST endpoints
├── downloader.py              # Multi-platform extraction engine & cleanup
├── requirements.txt           # Python package dependencies
├── run.bat                    # One-click Windows runner
├── README.md                  # Documentation
├── downloads/                 # Temporary downloads folder (auto-cleaned)
├── templates/
│   └── index.html             # Clean HTML5 web UI
└── static/
    ├── css/
    │   └── style.css          # Dark/Light theme stylesheet
    └── js/
        └── script.js          # Platform detection, theme switcher, & download logic
```

---

## ⚡ How to Run

### Method 1: One-Click Runner (Windows)
Double-click `run.bat` in the project folder:
📁 [run.bat](file:///C:/Users/devd1/Downloads/Projects/insta%20download/run.bat)

### Method 2: Command Line (PowerShell / Terminal)
```powershell
cd "C:\Users\devd1\Downloads\Projects\insta download"
python app.py
```
Then visit:
```text
http://127.0.0.1:5000
```
