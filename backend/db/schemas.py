from pydantic import BaseModel, EmailStr
from typing import Optional, List, Dict, Any
from datetime import datetime

# Auth Schemas
class UserCreate(BaseModel):
    email: EmailStr
    password: str
    full_name: Optional[str] = None

class UserResponse(BaseModel):
    id: int
    email: EmailStr
    full_name: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

# AI Detection Schemas
class DetectionResultResponse(BaseModel):
    id: Optional[int] = None
    image_url: str
    verdict: str
    confidence: float
    is_ai: bool
    explanation: Dict[str, Any]
    exif_data: Optional[Dict[str, Any]] = None
    heatmap_url: Optional[str] = None
    created_at: Optional[datetime] = None

# Comparison Schemas
class ComparisonResultResponse(BaseModel):
    id: Optional[int] = None
    image_a_url: str
    image_b_url: str
    overall_similarity: float
    verdict: str
    phash_distance: Optional[int] = None
    cosine_similarity: Optional[float] = None
    ssim_score: Optional[float] = None
    diff_heatmap_url: Optional[str] = None

# Reverse Search Schemas
class ReverseSearchMatch(BaseModel):
    source_url: str
    page_title: Optional[str] = None
    thumbnail_url: Optional[str] = None
    match_confidence: float
    domain_name: Optional[str] = None

class ReverseSearchResponse(BaseModel):
    scan_id: Optional[int] = None
    image_url: str
    total_matches: int
    matches: List[ReverseSearchMatch]

# Video Detection Schemas
class FrameAnalysis(BaseModel):
    timestamp_sec: float
    frame_index: int
    confidence: float
    is_ai: bool

class VideoDetectionResponse(BaseModel):
    video_url: str
    overall_verdict: str
    overall_confidence: float
    frames_analyzed: int
    frame_timeline: List[FrameAnalysis]
