# VeriPix — AI Image Verification & Search Platform

VeriPix is an integrated AI verification and forensic search platform designed to detect AI-generated images, compare visual duplicates with structural diff overlays, run web-scale reverse image searches, and analyze video content.

## Features

- **F1 — AI Image Detection**: Fast classifier identifying AI vs. real images with confidence scoring and Grad-CAM visual heatmaps.
- **F2 — Image Comparison**: Perceptual hashing (`pHash`), CLIP vector embeddings, and SSIM structural diff highlight overlay.
- **F3 — Reverse Image Search**: Web-scale source lookup powered by SerpApi / Google Vision with Redis caching.
- **F5 — Visual Explainability (Grad-CAM)**: Visual attention regions showing why an image was flagged.
- **F6 — EXIF & Metadata Forensics**: Metadata inspection flagging missing headers and editing software signatures.
- **F8 — Batch Processing**: Async bulk analysis for datasets and submission verification.
- **F9 — Video AI Detection**: Frame-sampling analysis with per-frame suspicion timelines.

## Project Structure

```
VeriPix/
├── backend/             # FastAPI backend server
│   ├── api/             # REST Endpoints (detect, compare, reverse-search, video, history)
│   ├── db/              # Database models, schemas, and connection
│   ├── ml/              # Machine Learning modules (detection, similarity, search, video)
│   └── main.py          # FastAPI application entry point
├── frontend/            # React + Vite frontend application
│   ├── src/             # Components, pages, and CSS design system
│   └── package.json     # Node dependencies
├── docs/                # Product, Architecture & Technical Specs
├── notebooks/           # Model training and exploration notebooks
└── tests/               # Unit and integration test suite
```

## Quickstart

### Backend Setup
```bash
cd backend
python -m venv venv
venv\Scripts\activate  # Windows
pip install -r requirements.txt
uvicorn main:app --reload
```

### Frontend Setup
```bash
cd frontend
npm install
npm run dev
```

## License
MIT
