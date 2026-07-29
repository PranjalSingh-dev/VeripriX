from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from db.database import get_db
from db.models import Scan

router = APIRouter(prefix="/history", tags=["Scan History"])

@router.get("")
def get_history(db: Session = Depends(get_db)):
    scans = db.query(Scan).order_by(Scan.created_at.desc()).limit(50).all()
    return [
        {
            "id": s.id,
            "image_url": s.image_url,
            "feature_type": s.feature_type,
            "verdict": s.verdict,
            "confidence": s.confidence,
            "created_at": s.created_at
        }
        for s in scans
    ]

@router.delete("/{scan_id}")
def delete_scan(scan_id: int, db: Session = Depends(get_db)):
    scan = db.query(Scan).filter(Scan.id == scan_id).first()
    if scan:
        db.delete(scan)
        db.commit()
        return {"status": "deleted", "scan_id": scan_id}
    return {"status": "not_found"}
