from fastapi import APIRouter, UploadFile, File, Depends
from sqlalchemy.orm import Session
from db.database import get_db
from db.schemas import ReverseSearchResponse, ReverseSearchMatch
from db.models import Scan, ReverseSearchResult
from ml.reverse_search.adapter import reverse_search_service

router = APIRouter(prefix="/reverse-search", tags=["Reverse Image Search"])

@router.post("", response_model=ReverseSearchResponse)
async def reverse_search(file: UploadFile = File(...), db: Session = Depends(get_db)):
    matches_raw = reverse_search_service.search_by_url(file.filename)
    
    scan = Scan(image_url=file.filename, feature_type="reverse_search", verdict=f"{len(matches_raw)} Matches Found")
    db.add(scan)
    db.commit()
    db.refresh(scan)

    match_objects = []
    for item in matches_raw:
        res = ReverseSearchResult(
            scan_id=scan.id,
            source_url=item["source_url"],
            page_title=item["page_title"],
            thumbnail_url=item["thumbnail_url"],
            match_confidence=item["match_confidence"],
            domain_name=item["domain_name"]
        )
        db.add(res)
        match_objects.append(ReverseSearchMatch(**item))
    
    db.commit()

    return ReverseSearchResponse(
        scan_id=scan.id,
        image_url=file.filename,
        total_matches=len(match_objects),
        matches=match_objects
    )
