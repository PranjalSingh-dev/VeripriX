# Tech Stack Document — VeriPix

## 1. Guiding Principle
This is a solo/small-team academic project. The stack favors: (a) free/open-source models where possible, (b) fast to build with, (c) things you can explain confidently in a viva/interview. Avoid over-engineering — build vs. buy is called out explicitly below.

---

## 2. Frontend
| Layer | Choice | Why |
|---|---|---|
| Framework | **React (Vite) + TypeScript** or **Next.js** | Next.js if you want SSR + easy API routes in one repo; plain React+Vite if backend is fully separate |
| Styling | **Tailwind CSS** | Fast to build clean UI, matches modern portfolio-quality expectations |
| Image upload/drag-drop | `react-dropzone` | Standard, well-documented |
| Image diff visualization | `react-compare-slider` or custom canvas overlay | For side-by-side / diff-highlight UI |
| State/data fetching | `TanStack Query (React Query)` | Handles async API calls, caching, loading states cleanly |

## 3. Backend
| Layer | Choice | Why |
|---|---|---|
| API framework | **FastAPI (Python)** | Best fit since all ML inference is Python-native; async support; auto-generates OpenAPI docs |
| Alternative | Node.js/Express if you want JS end-to-end and call Python ML services separately | Only if team is more comfortable in JS |
| Task queue | **Celery + Redis**, or simpler: **FastAPI BackgroundTasks** for MVP | Reverse-search + heavy inference should be async, not blocking the request |
| Auth | **JWT-based auth** via FastAPI or Supabase Auth / Firebase Auth | Keep it simple; don't build auth from scratch |

## 4. AI / ML Components (the core of the product)

### 4.1 AI-Generated Image Detection (Feature F1)
Two realistic approaches — pick one based on time budget:

**Option A (recommended for academic project): Use/fine-tune an existing open detector**
- Base on published open-source detectors such as **CLIP-based linear probe detectors** (e.g., "Universal Fake Detection" style approaches) or Hugging Face models tagged `ai-generated-image-detection` (several community models exist, e.g. `umm-maybe/AI-image-detector`, `Organika/sdxl-detector`).
- Fine-tune the final classification layer on a public dataset: **GenImage**, **DiffusionDB**, **CIFAKE**, or **ArtiFact** (all public, citable in your report).
- Framework: **PyTorch + Hugging Face Transformers/timm**.

**Option B (build your own, more "project-worthy" for a final year submission)**
- Use a **CNN backbone (ResNet50/EfficientNet)** or a **frequency-domain feature extractor** (FFT-based artifact detection — diffusion models leave detectable frequency-spectrum artifacts) + a classifier head.
- Train on GenImage/CIFAKE (real vs. fake pairs already labeled).
- This gives you a genuine "we built and trained a model" story for your report/viva, versus just calling an API.

> Recommendation: do Option B for the core model (good for your major-project grading), but keep Option A models as a fallback/ensemble to boost accuracy.

### 4.2 Image Comparison / Similarity (Feature F2)
Layered approach (cheap → expensive):
1. **Perceptual hashing** (`pHash`/`dHash` via the `imagehash` Python library) — instant, catches exact/near-exact duplicates (resize, compression, minor edits).
2. **Embedding-based similarity** using **CLIP (ViT-B/32)** or **DINOv2** embeddings + cosine similarity — catches semantic/edited duplicates (crop, filter, watermark, rotation).
3. **Structural diff** using `scikit-image`'s SSIM (Structural Similarity Index) to generate the visual diff overlay for near-duplicates.

### 4.3 Reverse Image Search (Feature F3)
This is the one component that is genuinely **build vs. buy**:
- **Buy (recommended):** Use an existing reverse-image-search API — **Google Cloud Vision API (Web Detection)**, **Bing Visual Search API**, **SerpApi (Google Lens engine)**, or **TinEye API**. Building a real web-scale reverse image search from scratch (crawling + indexing the internet) is not feasible for a student project.
- **Supplement (for the "project depth" grade):** Build your own **mini reverse-search over a small self-collected image corpus** using CLIP embeddings + a vector database (see below) — this shows you understand the underlying technique (embedding + nearest-neighbor search), even though production-scale search uses the paid API.

### 4.4 Vector Database (for embeddings — comparison + mini reverse-search)
- **FAISS** (local, free, great for a student project) or **Qdrant** / **Chroma** (if you want a hosted-service demo).

## 4.5 Video AI-Detection (Feature F9)
- **Frame extraction:** `OpenCV` (`cv2.VideoCapture`) or `ffmpeg-python` to sample frames at a fixed interval (e.g., 1 fps) — keep sampling rate low to control processing time/cost.
- **Per-frame inference:** reuse the F1 detection model (no separate training needed) on each sampled frame.
- **Aggregation:** simple majority vote or average confidence across frames for the overall verdict; keep the per-frame results to build the suspicion timeline.
- **Video formats:** support MP4/MOV/WebM; cap max video length/size for MVP (e.g., 60 seconds or 50 MB) to keep processing time reasonable on CPU.
- **Processing:** run as an async job (Celery/BackgroundTasks) — video processing takes longer than a single image, so this should never block the request thread.

## 5. Data Storage
| Need | Choice |
|---|---|
| Relational data (users, scan history, metadata) | **PostgreSQL** (or Supabase, which bundles Postgres + Auth + Storage) |
| Image file storage | **AWS S3** / **Cloudflare R2** / Supabase Storage (cheaper for a student budget) |
| Vector embeddings | FAISS index (local file) or Qdrant |
| Caching | **Redis** (cache repeated reverse-search queries to control API cost) |

## 6. Model Serving / Inference
- Serve PyTorch models via **FastAPI + TorchServe** or simply load model in-process for MVP scale.
- Use **ONNX Runtime** to export the trained detector for faster CPU inference if you don't have GPU hosting in production.

## 7. Deployment
| Component | Suggested host | Why |
|---|---|---|
| Frontend | **Vercel** or **Netlify** | Free tier, trivial CI/CD for React/Next.js |
| Backend API | **Railway**, **Render**, or a small **AWS EC2/Lightsail** | Free/cheap tiers suitable for student projects |
| ML inference (if GPU needed for training only, not serving) | **Google Colab / Kaggle** for training; CPU inference in production is fine for a single-image-at-a-time detector |
| Database | Supabase (free tier) or Railway Postgres | |
| CI/CD | GitHub Actions | Free for public repos |

## 8. Suggested Repo Structure
```
veripix/
├── frontend/            # React/Next.js app
├── backend/
│   ├── api/             # FastAPI routes
│   ├── ml/
│   │   ├── detection/   # AI-image detector training + inference code
│   │   ├── similarity/  # embedding + hashing comparison logic
│   │   └── reverse_search/ # wrapper around chosen search API
│   ├── db/               # models, migrations
│   └── workers/          # Celery tasks
├── notebooks/            # training/experiment notebooks
├── docs/                 # PRD.md, TECH_STACK.md, ARCHITECTURE.md
└── tests/
```

## 9. Third-Party APIs & Costs to Plan For
- Google Cloud Vision API — pay-per-call after free quota.
- Bing Visual Search / SerpApi — paid, has free trial credits.
- Budget for these as a "reverse search" line item; cache aggressively with Redis to avoid repeat costs on the same image.
