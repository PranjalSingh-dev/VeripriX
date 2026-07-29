# Weekly Roadmap — VeriPix (3-Month Solo Build Plan)

Assumes a solo build, working roughly evenings/weekends-equivalent effort each week. Adjust pace as needed — the order (not the exact week count) is the important part: get the core detection model working *before* polishing UI, since it's the highest-risk, most novel part of the project.

---

## Month 1 — Foundations + Core AI Detection (F1)

### Week 1: Research & Setup
- Finalize app name, scope, and feature list (use PRD.md as the source of truth).
- Research and download datasets for AI-detection training: **CIFAKE** (easiest to start with, already labeled real/fake), **GenImage** or **DiffusionDB** (larger, more diverse).
- Set up GitHub repo with the folder structure from ARCHITECTURE.md.
- Set up Python environment (PyTorch, torchvision, transformers, scikit-image, imagehash).
- Set up a Google Colab/Kaggle notebook for model training (free GPU access).
- **Deliverable:** repo scaffolded, dataset downloaded and explored (class balance, image sizes, sample visualization).

### Week 2: Backend Skeleton
- Set up FastAPI project structure (`api/`, `db/`, `ml/`).
- Set up PostgreSQL (locally or via Supabase free tier).
- Define DB schema: `users`, `scans`, `comparisons`, `reverse_search_results`.
- Implement basic auth (JWT) — register/login endpoints.
- Set up file upload endpoint with validation (file type, size limit) and object storage (S3/R2/Supabase Storage).
- **Deliverable:** you can register, log in, and upload an image via API (e.g., tested with Postman/curl) that gets stored and a DB row created.

### Week 3: Baseline AI-Detection Model (v1)
- Train a baseline CNN classifier (ResNet18/EfficientNet-B0 via transfer learning) on CIFAKE: real vs. AI-generated.
- Evaluate accuracy, precision/recall, confusion matrix on a held-out test set.
- Export the trained model (`.pt` or ONNX).
- **Deliverable:** a working baseline model with a documented accuracy number (this is your first real result — write it down for your report).

### Week 4: Improve Detection Model + Wrap as API
- Improve the model: try a CLIP-based linear probe, or add frequency-domain features (FFT-based artifact detection) as a second signal; consider a simple ensemble of two models.
- Write inference code: preprocess → model forward pass → confidence score.
- Wrap it as a FastAPI endpoint: `POST /api/detect`.
- Connect this endpoint to actually save results in the `scans` table.
- **Deliverable:** `/api/detect` works end-to-end — upload image via API, get back `{label, confidence}`, and it's stored in the DB.

---

## Month 2 — Comparison (F2), Reverse Search (F3), and Frontend

### Week 5: Image Comparison Engine — Hashing + Embeddings
- Implement perceptual hashing (`imagehash` library) for fast near-duplicate detection.
- Implement CLIP (ViT-B/32) embedding extraction + cosine similarity for semantic-level comparison.
- Test both on a self-made set of image pairs (original, cropped, filtered, watermarked, unrelated) to see how each method performs.
- **Deliverable:** a working comparison function that takes 2 images and returns a similarity score.

### Week 6: Comparison — Diff Visualization + API
- Add SSIM-based structural diff to generate a visual "what changed" heatmap between two similar images.
- Wrap as `POST /api/compare` endpoint (accepts 2+ images, returns similarity score, verdict, diff image).
- Save results to `comparisons` table.
- **Deliverable:** `/api/compare` works end-to-end with real test image pairs.

### Week 7: Reverse Image Search Integration
- Choose a provider (start with **SerpApi's free trial credits** or **Google Vision Web Detection**, whichever gives easier initial access) and get API keys.
- Build the Reverse Search Adapter that normalizes the provider's response into your internal schema.
- Add Redis for caching results by image hash (avoid duplicate paid calls).
- Wrap as an async endpoint: `POST /api/reverse-search` + `GET /api/reverse-search/{job_id}`.
- **Deliverable:** uploading an image returns a list of similar sources found online.

### Week 8: Frontend Skeleton + Core Pages
- Set up React (Vite) or Next.js project with Tailwind CSS.
- Build: upload page (drag-drop), results page (detection verdict + confidence), comparison page (side-by-side + diff overlay), reverse-search results page (thumbnail grid).
- Wire up API calls with TanStack Query; handle loading/error states.
- **Deliverable:** you can use the full app end-to-end from the browser — upload, detect, compare, reverse-search — even if styling is rough.

---

## Month 3 — Added Features, Polish, Testing, Deployment

### Week 9: Explainability (F5) + Metadata Analysis (F6) + Video Detection (F9)
- Add Grad-CAM (or similar) visualization for the detection model so users can see *which region* triggered the AI verdict.
- Add EXIF metadata extraction (`Pillow`/`exifread`) and display camera info / flag missing EXIF as a supporting signal.
- Add video support: frame extraction (OpenCV/ffmpeg) at 1 fps, run each frame through the existing F1 model, aggregate into an overall verdict + a per-frame confidence timeline chart. Cap video length/size for MVP.
- **Deliverable:** detection results page now shows a heatmap overlay + metadata panel; a new video-upload flow returns an overall verdict with a suspicion timeline.

### Week 10: History, Shareable Reports (F7), Batch Upload (F8)
- Build the "My History" page (list of past scans, filter by type/date).
- Build shareable report generation: a public link (and optionally PDF export) summarizing all results for one image.
- Add batch upload: accept multiple files, process as an async job, show progress, allow CSV export of results.
- **Deliverable:** all F1–F8 features are present in the app, even if some are basic.

### Week 11: UI Polish + Bug Fixing
- Full UI pass: consistent styling, responsive/mobile layout, empty states, error states, loading skeletons.
- Cross-browser test; fix upload edge cases (huge files, corrupted files, unsupported formats).
- Add rate limiting to protect reverse-search API cost.
- Write basic automated tests for the core API endpoints (detect/compare/reverse-search).
- **Deliverable:** app feels stable and presentable, not just functional.

### Week 12: Deployment + Documentation + Demo Prep
- Deploy frontend (Vercel/Netlify) and backend (Railway/Render).
- Final accuracy benchmarking on the AI-detection model — document the number clearly for your report.
- Write/finalize your project report using the PRD, tech stack, and architecture docs as the base, plus what actually changed during the build (be honest about what you simplified or descoped — that's normal and expected).
- Prepare a demo script: 3–5 example images that clearly show each feature working (one obvious AI image, one obvious real photo, one edited duplicate pair, one image with online matches).
- **Deliverable:** deployed, working app + final report + demo-ready.

---

## Tips for Staying on Track
- **De-risk the hardest part first.** The AI-detection model (Month 1) is the most uncertain part — get *something* working by Week 4, even if accuracy isn't perfect yet. Everything else is comparatively standard web-dev work.
- **Keep a running log of accuracy numbers and design decisions** from Week 1 onward — this becomes 80% of your final report with almost no extra writing at the end.
- **If a week runs over, protect Weeks 1–8 (the core three features) and cut from Weeks 9–11 (F5–F9) first** — those are explicitly the "added features," not the core deliverable.
- **Week 9 is the heaviest week now (F5 + F6 + F9 together)** — if it doesn't fit in one week, split it: do F9 (video) first since it mostly reuses F1 with no new model work, then F5/F6 the following week, sliding Week 10–12 back by a few days rather than cutting scope.
- Commit to GitHub weekly with clear commit messages — useful both as a safety net and as evidence of steady progress if anyone (a mentor/evaluator) checks your repo history.
