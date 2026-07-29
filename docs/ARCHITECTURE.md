# Architecture Document — VeriPix

## 1. High-Level System Diagram (textual)

```
┌─────────────┐        HTTPS         ┌────────────────────┐
│   Frontend   │ ───────────────────▶│    API Gateway /    │
│ (React/Next) │◀─────────────────── │   FastAPI Backend   │
└─────────────┘        JSON          └─────────┬──────────┘
                                                │
                 ┌──────────────────────────────┼───────────────────────────┐
                 │                              │                           │
                 ▼                              ▼                           ▼
        ┌──────────────────┐         ┌────────────────────┐       ┌──────────────────┐
        │ AI Detection      │         │ Similarity Engine   │       │ Reverse Search    │
        │ Service           │         │ (hash + CLIP embed  │       │ Adapter           │
        │ (PyTorch model)   │         │  + SSIM diff)        │       │ (Vision/Bing API) │
        └────────┬──────────┘         └─────────┬───────────┘       └────────┬──────────┘
                 │                              │                            │
                 ▼                              ▼                            ▼
        ┌───────────────────────────────────────────────────────────────────────┐
        │                     Shared Services Layer                             │
        │  - Object Storage (S3/R2) for uploaded images                         │
        │  - PostgreSQL (users, scan history, verdicts)                        │
        │  - FAISS/Qdrant vector index (embeddings)                            │
        │  - Redis (cache + job queue for async reverse-search calls)          │
        └───────────────────────────────────────────────────────────────────────┘
```

## 2. Component Responsibilities

### 2.1 Frontend
- Upload UI (drag-drop, URL paste), results dashboard, history view, comparison side-by-side view with diff overlay.
- Calls backend REST API; polls or uses WebSocket/SSE for async reverse-search jobs.

### 2.2 API Gateway / Backend (FastAPI)
- Auth (JWT), request validation, file-type/size checks, rate limiting.
- Routes requests to the three ML services (can be in-process modules initially, split into microservices later if needed).
- Persists scan results to Postgres; stores image files in object storage (or discards after processing, per privacy policy).

### 2.3 AI Detection Service
- Loads the trained classifier (ResNet/EfficientNet + frequency features, or fine-tuned CLIP probe).
- Input: image → preprocessing (resize/normalize) → model forward pass → output: label + confidence.
- Runs as a synchronous call for MVP (should return in a few seconds on CPU for a single image); can be moved to a queued job if load increases.

### 2.4 Similarity Engine
- Step 1: compute perceptual hash for each image, compare Hamming distance (fast rejection for "definitely different" images).
- Step 2: compute CLIP/DINOv2 embedding for each image, compare cosine similarity (semantic-level match).
- Step 3: if similarity is high, run SSIM-based pixel diff to generate a visual "what changed" heatmap.
- Output: similarity score (0-100), verdict category, optional diff image.

### 2.5 Reverse Search Adapter
- Wraps the chosen external API (Google Vision Web Detection / Bing Visual Search / SerpApi).
- Normalizes the different providers' response formats into one internal schema: `{source_url, thumbnail_url, match_confidence, page_title}`.
- Runs as an **async background job** (Celery/BackgroundTasks) since external API latency can be a few seconds and you don't want to block the main request thread.
- Results cached in Redis keyed by image hash, to avoid repeat paid calls for the same image.

### 2.6 Video Detection Service (F9)
- Runs as an async job: extracts frames at a fixed interval → sends each frame through the AI Detection Service (2.3) → aggregates per-frame results into an overall verdict + timeline.
- Reuses the existing detection model — no new model training required, just an orchestration layer around it.
- Enforces max video length/size (MVP cap) to keep processing time bounded on CPU.

### 2.7 Data Layer
- **PostgreSQL schema (core tables):**
  - `users (id, email, created_at, ...)`
  - `scans (id, user_id, image_url, feature_type[detection|comparison|reverse_search], result_json, created_at)`
  - `comparisons (id, scan_id, image_a_url, image_b_url, similarity_score, verdict)`
  - `reverse_search_results (id, scan_id, source_url, thumbnail_url, match_confidence)`
- **Object storage:** raw uploaded images (short retention policy — e.g., auto-delete after 30 days unless user saves to history).
- **Vector index (FAISS/Qdrant):** stores embeddings for the self-built "mini reverse search" demo corpus, and optionally for fast duplicate-detection across a user's own history.

## 3. Data Flow — Example: "Compare two images"
1. User uploads Image A and Image B via frontend.
2. Frontend sends both to `POST /api/compare`.
3. Backend validates files, stores them in object storage, gets back URLs.
4. Backend calls Similarity Engine: hash compare → embedding compare → (if needed) SSIM diff.
5. Backend saves result row in `comparisons` table.
6. Backend returns `{similarity_score, verdict, diff_image_url}` to frontend.
7. Frontend renders side-by-side view + diff overlay.

## 4. Data Flow — Example: "Reverse search this image"
1. User uploads Image → `POST /api/reverse-search`.
2. Backend computes an image hash; checks Redis cache — if hit, return cached results instantly.
3. If cache miss: backend enqueues an async job → Reverse Search Adapter calls external API.
4. Job completes → results normalized → saved to `reverse_search_results` + cached in Redis.
5. Frontend polls `GET /api/reverse-search/{job_id}` (or receives via WebSocket) and renders result list.

## 5. API Endpoints (draft)
| Method | Endpoint | Purpose |
|---|---|---|
| POST | `/api/detect` | Upload image → AI vs real verdict + confidence |
| POST | `/api/compare` | Upload 2+ images → similarity scores + diff |
| POST | `/api/reverse-search` | Upload image → enqueue reverse search job |
| GET | `/api/reverse-search/{job_id}` | Poll/fetch reverse search results |
| POST | `/api/detect-video` | Upload video → enqueue frame-sampling + detection job |
| GET | `/api/detect-video/{job_id}` | Poll/fetch video verdict + per-frame confidence timeline |
| GET | `/api/history` | Get logged-in user's past scans |
| DELETE | `/api/history/{scan_id}` | Delete a scan record + associated image |
| POST | `/api/auth/login`, `/api/auth/register` | Auth |

## 6. Scalability & Reliability Notes
- Keep ML inference stateless so multiple backend instances can run behind a load balancer.
- Reverse-search cost is the main scaling risk — Redis caching + per-user rate limits are essential from day one, not an afterthought.
- Model versioning: tag each detection model version in the `scans` table result so you can track accuracy drift as generators evolve and you retrain.
- Add a feedback loop: let users flag a wrong verdict — feed this into a review queue for future model retraining (great talking point for your project report).

## 7. Security & Privacy Notes
- Validate file type by content (magic bytes), not just extension.
- Scan uploads for malware before processing.
- Strip EXIF/location metadata from stored images unless needed.
- Clear data-retention policy: state how long images/history are kept and give users a delete option.
- Rate-limit per IP/user to prevent abuse of paid reverse-search calls.

## 8. Suggested Build Order (maps to PRD milestones)
1. Backend skeleton (FastAPI) + Postgres + auth.
2. AI Detection Service (train/fine-tune model offline in a notebook, then wrap as an inference endpoint).
3. Similarity Engine (hash → embeddings → SSIM diff).
4. Reverse Search Adapter (start with one provider, e.g., SerpApi's free trial).
5. Frontend integration for all three features + history view.
6. Caching, rate limiting, deployment, and final report/documentation.
