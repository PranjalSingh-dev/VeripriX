import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, JSON, Enum, Text
from sqlalchemy.orm import relationship
import enum
from db.database import Base

class FeatureType(str, enum.Enum):
    DETECTION = "detection"
    COMPARISON = "comparison"
    REVERSE_SEARCH = "reverse_search"
    VIDEO_DETECTION = "video_detection"

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    scans = relationship("Scan", back_populates="user", cascade="all, delete-orphan")

class Scan(Base):
    __tablename__ = "scans"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    image_url = Column(String, nullable=False)
    feature_type = Column(String, nullable=False)
    verdict = Column(String, nullable=True) # e.g. "AI-Generated", "Real", "Identical", "Near-Duplicate"
    confidence = Column(Float, nullable=True)
    result_metadata = Column(JSON, nullable=True) # EXIF, heatmap paths, frame timings
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    user = relationship("User", back_populates="scans")
    comparisons = relationship("Comparison", back_populates="scan", cascade="all, delete-orphan")
    reverse_results = relationship("ReverseSearchResult", back_populates="scan", cascade="all, delete-orphan")

class Comparison(Base):
    __tablename__ = "comparisons"

    id = Column(Integer, primary_key=True, index=True)
    scan_id = Column(Integer, ForeignKey("scans.id"), nullable=False)
    image_a_url = Column(String, nullable=False)
    image_b_url = Column(String, nullable=False)
    phash_distance = Column(Integer, nullable=True)
    cosine_similarity = Column(Float, nullable=True)
    ssim_score = Column(Float, nullable=True)
    overall_similarity = Column(Float, nullable=False)
    verdict = Column(String, nullable=False)
    diff_heatmap_url = Column(String, nullable=True)

    scan = relationship("Scan", back_populates="comparisons")

class ReverseSearchResult(Base):
    __tablename__ = "reverse_search_results"

    id = Column(Integer, primary_key=True, index=True)
    scan_id = Column(Integer, ForeignKey("scans.id"), nullable=False)
    source_url = Column(String, nullable=False)
    page_title = Column(String, nullable=True)
    thumbnail_url = Column(String, nullable=True)
    match_confidence = Column(Float, default=1.0)
    domain_name = Column(String, nullable=True)

    scan = relationship("Scan", back_populates="reverse_results")
