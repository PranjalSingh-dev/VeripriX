"""
Integration Tests for FastAPI REST Endpoints
Tests all core API routes: /detect, /compare, /reverse-search, /detect-video, /history
"""
import sys
import os
import io
import pytest
from fastapi.testclient import TestClient
from PIL import Image

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from main import app

client = TestClient(app)


def _make_image_bytes(color=(100, 150, 200), size=(256, 256), fmt="JPEG"):
    img = Image.new("RGB", size, color=color)
    buf = io.BytesIO()
    img.save(buf, format=fmt)
    buf.seek(0)
    return buf


class TestHealthEndpoint:
    def test_root_returns_200(self):
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert data["status"] == "online"

    def test_health_check(self):
        response = client.get("/api/health")
        assert response.status_code == 200
        assert response.json()["status"] == "healthy"


class TestDetectEndpoint:
    def test_detect_valid_image_returns_200(self):
        img_bytes = _make_image_bytes()
        response = client.post(
            "/api/detect",
            files={"file": ("test_photo.jpg", img_bytes, "image/jpeg")}
        )
        assert response.status_code == 200

    def test_detect_response_has_verdict(self):
        img_bytes = _make_image_bytes()
        response = client.post(
            "/api/detect",
            files={"file": ("test_photo.jpg", img_bytes, "image/jpeg")}
        )
        data = response.json()
        assert "verdict" in data
        assert "confidence" in data
        assert "is_ai" in data

    def test_detect_confidence_between_0_and_100(self):
        img_bytes = _make_image_bytes()
        response = client.post(
            "/api/detect",
            files={"file": ("test_photo.jpg", img_bytes, "image/jpeg")}
        )
        data = response.json()
        assert 0.0 <= data["confidence"] <= 100.0

    def test_detect_invalid_file_type_returns_400(self):
        txt_buf = io.BytesIO(b"this is text data, not an image")
        response = client.post(
            "/api/detect",
            files={"file": ("text.txt", txt_buf, "text/plain")}
        )
        assert response.status_code == 400


class TestCompareEndpoint:
    def test_compare_two_identical_images(self):
        img_bytes_a = _make_image_bytes(color=(200, 100, 50))
        img_bytes_b = _make_image_bytes(color=(200, 100, 50))
        response = client.post(
            "/api/compare",
            files={
                "file_a": ("img_a.jpg", img_bytes_a, "image/jpeg"),
                "file_b": ("img_b.jpg", img_bytes_b, "image/jpeg"),
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert "verdict" in data
        assert "overall_similarity" in data

    def test_compare_response_has_all_metrics(self):
        img_bytes_a = _make_image_bytes(color=(50, 80, 200))
        img_bytes_b = _make_image_bytes(color=(200, 100, 50))
        response = client.post(
            "/api/compare",
            files={
                "file_a": ("img_a.jpg", img_bytes_a, "image/jpeg"),
                "file_b": ("img_b.jpg", img_bytes_b, "image/jpeg"),
            }
        )
        data = response.json()
        assert "phash_distance" in data
        assert "cosine_similarity" in data
        assert "ssim_score" in data


class TestReverseSearchEndpoint:
    def test_reverse_search_valid_image(self):
        img_bytes = _make_image_bytes()
        response = client.post(
            "/api/reverse-search",
            files={"file": ("test_photo.jpg", img_bytes, "image/jpeg")}
        )
        assert response.status_code == 200
        data = response.json()
        assert "total_matches" in data
        assert "matches" in data
        assert isinstance(data["matches"], list)


class TestHistoryEndpoint:
    def test_history_returns_list(self):
        response = client.get("/api/history")
        assert response.status_code == 200
        assert isinstance(response.json(), list)

    def test_delete_nonexistent_scan_returns_not_found(self):
        response = client.delete("/api/history/999999")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "not_found"
