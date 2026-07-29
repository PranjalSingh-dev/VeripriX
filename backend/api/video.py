from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from sqlalchemy.orm import Session
from db.database import get_db
from db.schemas import VideoDetectionResponse
from db.models import Scan
from ml.video.frame_extractor import video_service

router = APIRouter(prefix="/detect-video", tags=["Video AI Detection"])

@router.post("", response_model=VideoDetectionResponse)
async def detect_video(file: UploadFile = File(...), db: Session = Depends(get_db)):
    if not file.content_type.startswith("video/"):
        raise HTTPException(status_code=400, detail="File uploaded must be a video format (MP4/WebM/MOV)")

    contents = await file.read()
    result = video_service.process_video_bytes(contents, sample_fps=1.0)

    scan = Scan(
        image_url=file.filename,
        feature_type="video_detection",
        verdict=result["overall_verdict"],
        confidence=result["overall_confidence"],
        result_metadata={
            "frames_analyzed": result["frames_analyzed"],
            "timeline": result["frame_timeline"]
        }
    )
    db.add(scan)
    db.commit()

    return VideoDetectionResponse(
        video_url=file.filename,
        overall_verdict=result["overall_verdict"],
        overall_confidence=result["overall_confidence"],
        frames_analyzed=result["frames_analyzed"],
        frame_timeline=result["frame_timeline"]
    )
