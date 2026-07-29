from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from sqlalchemy.orm import Session
from db.database import get_db
from db.schemas import ComparisonResultResponse
from db.models import Scan, Comparison
from ml.similarity.hasher import hasher_service
from ml.similarity.embeddings import embedding_service
from ml.similarity.ssim_diff import ssim_service

router = APIRouter(prefix="/compare", tags=["Image Comparison"])

@router.post("", response_model=ComparisonResultResponse)
async def compare_images(
    file_a: UploadFile = File(...),
    file_b: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    contents_a = await file_a.read()
    contents_b = await file_b.read()

    # Perceptual hash distance
    hashes_a = hasher_service.compute_hashes(contents_a)
    hashes_b = hasher_service.compute_hashes(contents_b)
    phash_dist = hasher_service.compare_hashes(hashes_a["phash"], hashes_b["phash"])

    # Vector embedding cosine similarity
    emb_a = embedding_service.extract_embedding(contents_a)
    emb_b = embedding_service.extract_embedding(contents_b)
    cosine_sim = embedding_service.compute_cosine_similarity(emb_a, emb_b)

    # SSIM difference heatmap
    ssim_res = ssim_service.compute_ssim_diff(contents_a, contents_b)

    # Calculate aggregate similarity score (0 - 100%)
    overall_sim = round(float(cosine_sim * 70 + (1 - min(phash_dist, 64) / 64) * 30), 2)
    
    if overall_sim >= 95.0:
        verdict = "Identical Images"
    elif overall_sim >= 70.0:
        verdict = "Near-Duplicate (Edited / Cropped / Filtered)"
    else:
        verdict = "Different Images"

    # Save to database
    scan = Scan(image_url=f"{file_a.filename} vs {file_b.filename}", feature_type="comparison", verdict=verdict, confidence=overall_sim)
    db.add(scan)
    db.commit()
    db.refresh(scan)

    comp = Comparison(
        scan_id=scan.id,
        image_a_url=file_a.filename,
        image_b_url=file_b.filename,
        phash_distance=phash_dist,
        cosine_similarity=round(float(cosine_sim), 4),
        ssim_score=ssim_res["ssim_score"],
        overall_similarity=overall_sim,
        verdict=verdict,
        diff_heatmap_url=ssim_res["diff_heatmap_url"]
    )
    db.add(comp)
    db.commit()

    return ComparisonResultResponse(
        id=scan.id,
        image_a_url=file_a.filename,
        image_b_url=file_b.filename,
        overall_similarity=overall_sim,
        verdict=verdict,
        phash_distance=phash_dist,
        cosine_similarity=round(float(cosine_sim), 4),
        ssim_score=ssim_res["ssim_score"],
        diff_heatmap_url=ssim_res["diff_heatmap_url"]
    )
