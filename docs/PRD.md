# Product Requirements Document (PRD)
## Project Name (working title): VeriPix — AI Image Verification & Search Platform
*(rename freely — "PixelProof", "ImageLens", "TrueFrame" are other options)*

**Author:** Pranjal Singh
**Version:** 1.0
**Date:** July 2026

---

## 1. Problem Statement
AI-generated images (from Midjourney, DALL·E, Stable Diffusion, Flux, etc.) are now visually indistinguishable from real photos to the average person. This creates three practical problems for everyday users, journalists, recruiters, and students:

1. **Trust gap** — no easy way to check if an image is AI-generated or a real photograph.
2. **Duplication/plagiarism gap** — no easy way to check if two or more images are the same image (or manipulated/re-edited versions of each other).
3. **Provenance gap** — no easy way to find where an image originally came from or where else it appears online.

## 2. Product Vision
A single web app/API where a user uploads or pastes an image and gets three answers back:
- **Is this AI-generated or real?** (with a confidence score)
- **Is this the same as another image I have?** (similarity score + what changed)
- **Where else does this image appear on the internet?** (reverse image search results)

## 3. Target Users
| Persona | Need |
|---|---|
| General user | "Is this photo I saw on WhatsApp/Instagram real or AI?" |
| Journalist/fact-checker | Verify authenticity of a viral image before reporting |
| Recruiter/HR | Check if a candidate's profile photo is AI-generated |
| Student/researcher | Detect duplicate/plagiarized images in a dataset or report |
| E-commerce/content team | Find where a product image is being used across the web |

## 4. Core Features (MVP Scope)

### F1 — AI-Generated Image Detection
- User uploads an image (JPG/PNG/WebP).
- System returns: **Real** or **AI-Generated**, with a confidence percentage (e.g., "92% likely AI-generated").
- Show which signal contributed (e.g., noise pattern, metadata, frequency artifacts) — optional "explain" section for transparency.
- Support common generators: Midjourney, DALL·E, Stable Diffusion/Flux family, plus general GAN/diffusion detection (not generator-specific).

### F2 — Image Comparison (Same/Different Detection)
- User uploads 2+ images.
- System returns a **similarity score (0–100%)** and a verdict: *Identical*, *Near-duplicate (edited/cropped/filtered)*, or *Different*.
- Highlight regions that differ (visual diff overlay) for near-duplicates.
- Handle common transformations: resize, crop, compression, watermark, color/filter change, rotation.

### F3 — Reverse Image Search
- User uploads an image.
- System searches the web and returns a list of pages/sources where a visually similar image appears, with thumbnail, source URL, and match confidence.
- De-duplicate results from the same domain; sort by similarity.

### F4 — Unified Report (nice-to-have, post-MVP)
- Combine F1+F2+F3 into a single shareable "Image Report" (PDF/link) — useful for journalists/recruiters.

### F5 — Explainability / "Why did it say that?" (added for 3-month build)
- For AI-detection results, show a visual heatmap (Grad-CAM style) over the regions of the image that most influenced the verdict.
- Builds user trust and is a strong talking point for a project report/viva — shows you understand your own model, not just its output.

### F6 — Metadata / EXIF Analysis (added for 3-month build)
- Read and display EXIF data (camera model, GPS, timestamp, editing software tags) when present.
- Flag suspicious signals: missing EXIF entirely (common in AI-generated images and screenshots), or signs of re-encoding/editing software.
- Used as a *supporting* signal alongside the ML verdict, not a standalone determination.

### F7 — Shareable Verification Report (added for 3-month build)
- Generate a public shareable link (and optional PDF/QR code) summarizing all checks run on an image — verdict, confidence, comparison results, reverse-search hits.
- Useful for journalists/recruiters who need to send "here's the proof" to someone else.

### F8 — Batch / Bulk Upload (added for 3-month build)
- Allow uploading a folder or multiple images at once (e.g., 10–20) and running detection/comparison across the whole batch.
- Useful for researchers/students checking a dataset or a set of submissions for duplicates/AI content.
- Runs as an async batch job with a progress bar; results downloadable as CSV.

### F9 — Video AI-Detection (added feature)
- User uploads a short video (or pastes a video URL) instead of a single image.
- System samples frames at a fixed interval (e.g., 1 frame/second), runs the existing AI-detection model (F1) on each sampled frame, then aggregates into an overall verdict.
- Output: overall "AI-generated / Real / Mixed" verdict + a per-frame confidence timeline (e.g., a small chart showing which timestamps look most suspicious).
- Practical scope note: this reuses your F1 image detector rather than requiring a separate temporal/deepfake model — genuinely buildable in the 3-month window, and a good "extra feature" talking point, while a full frame-by-frame deepfake/lip-sync detector is a separate, much larger research problem (kept as stretch, see below).

### Stretch features (beyond 3 months, mention as future work in report)
- Browser extension (right-click an image anywhere → "Check with VeriPix").
- Public developer API with API keys and usage dashboard.
- Embeddable "Verified" badge/widget for websites.
- Full deepfake detection (temporal/lip-sync/face-swap specific models) — F9 above only checks per-frame "AI-generated look," not face-swap deepfakes specifically.

## 5. User Stories
- As a user, I want to drag-and-drop an image so I can instantly check if it's AI-generated.
- As a user, I want to upload two images side-by-side so I can see if they're the same photo.
- As a user, I want to see where an image appears online so I can trace its original source.
- As a user, I want a confidence score, not just a yes/no, so I can judge how much to trust the result.
- As a returning user, I want my past checks saved (history) so I can revisit them.

## 6. Functional Requirements
1. Accept image upload via file, URL paste, and drag-and-drop.
2. Support JPG, PNG, WebP, HEIC (convert internally); max file size configurable (e.g., 10 MB).
3. Return AI-detection verdict within ~3–5 seconds for a single image.
4. Support comparing up to 5 images in one batch.
5. Reverse search must query at least one external image-search backend (see Tech Stack doc) and return top 10–20 results.
6. Store user's scan history (if logged in) with timestamp, thumbnail, and verdicts.
7. Provide a public API (rate-limited) so the detection/comparison logic can be reused (e.g., for a Chrome extension later).
8. Graceful handling of unsupported formats, corrupted files, and NSFW images (blur + warn, don't hard-block unless policy requires).

## 7. Non-Functional Requirements
- **Accuracy:** AI-detection target ≥ 85% accuracy on a public benchmark (e.g., subsets of GenImage/DiffusionDB); be transparent that no detector is 100% accurate.
- **Performance:** p95 response time < 5s per image for detection/comparison; reverse search < 8s.
- **Scalability:** stateless API layer, horizontally scalable; async job queue for heavier reverse-search calls.
- **Privacy:** uploaded images should not be stored beyond what's needed for history; clear deletion option; no image reused for model training without consent.
- **Security:** signed upload URLs, file-type validation, virus/malware scan on upload, rate limiting to prevent abuse.
- **Availability:** 99% uptime target for MVP.
- **Cost control:** reverse-image-search APIs are usually paid per call — needs quota/caching strategy.

## 8. Out of Scope (MVP)
- Full deepfake detection (face-swap/lip-sync-specific models) — F9 covers frame-level "AI-generated look" detection on video, not specialized deepfake forensics.
- Detecting *which specific* AI model generated an image (only real vs AI-generated).
- Browser extension (planned as a fast-follow, not MVP).
- Legal/forensic-grade certification of authenticity (this is an assistive tool, not legal proof).

## 9. Success Metrics
- Detection accuracy on benchmark test set.
- Average response latency per feature.
- Number of images processed / day (usage).
- User retention (returning users using history feature).
- % of reverse-search queries returning at least one relevant match.

## 10. Timeline
This is now planned as a **12-week (3-month) solo build**. See the separate **WEEKLY_ROADMAP.md** for the full week-by-week breakdown of what to build, in what order, including F5–F8.

## 11. Risks / Open Questions
- AI-detection models degrade fast as new generators appear — needs a retraining/update plan.
- True reverse image search (crawling the whole web) is not feasible to build from scratch — will likely need a paid API (Google Vision, Bing Visual Search, SerpApi, TinEye) rather than self-hosted crawling. This is a **build vs. buy** decision — see Tech Stack doc.
- Copyright/ToS: scraping search engines directly can violate their terms; using official APIs is the safe path.
