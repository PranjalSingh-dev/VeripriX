from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from sqlalchemy.orm import Session
from db.database import get_db
from db.schemas import DetectionResultResponse
from db.models import Scan
from ml.detection.detector import detector_service
from ml.detection.gradcam import gradcam_service
from ml.metadata.exif_scanner import exif_service

router = APIRouter(prefix="/detect", tags=["AI Detection"])

@router.post("", response_model=DetectionResultResponse)
async def detect_image(file: UploadFile = File(...), db: Session = Depends(get_db)):
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="File uploaded must be an image")

    contents = await file.read()
    
    # Run ML Detection & Features
    detection = detector_service.predict(contents)
    exif_res = exif_service.scan_bytes(contents)
    heatmap_url = gradcam_service.generate_heatmap(contents)

    # Persist Scan record
    scan = Scan(
        image_url=file.filename,
        feature_type="detection",
        verdict=detection["verdict"],
        confidence=detection["confidence"],
        result_metadata={
            "explanation": detection["explanation"],
            "exif": exif_res,
            "has_heatmap": bool(heatmap_url)
        }
    )
    db.add(scan)
    db.commit()
    db.refresh(scan)

    return DetectionResultResponse(
        id=scan.id,
        image_url=file.filename,
        verdict=detection["verdict"],
        confidence=detection["confidence"],
        is_ai=detection["is_ai"],
        explanation=detection["explanation"],
        exif_data=exif_res,
        heatmap_url=heatmap_url,
        created_at=scan.created_at
    )
