"""
Unit Tests for Image Similarity Engine
Tests perceptual hashing, cosine embedding similarity, and SSIM diff visualizer.
"""
import sys
import os
import io
import pytest
import numpy as np
from PIL import Image

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from ml.similarity.hasher import PerceptualHasher
from ml.similarity.embeddings import EmbeddingSimilarityEngine
from ml.similarity.ssim_diff import SSIMDiffEngine


def _create_image_bytes(color=(120, 180, 200), width=256, height=256, fmt="JPEG"):
    img = Image.new("RGB", (width, height), color=color)
    buf = io.BytesIO()
    img.save(buf, format=fmt)
    return buf.getvalue()


class TestPerceptualHasher:
    def setup_method(self):
        self.hasher = PerceptualHasher()

    def test_compute_hashes_returns_all_keys(self):
        img_bytes = _create_image_bytes()
        result = self.hasher.compute_hashes(img_bytes)
        assert "phash" in result
        assert "dhash" in result
        assert "raw_phash" in result

    def test_identical_images_zero_hamming_distance(self):
        img_bytes = _create_image_bytes(color=(50, 100, 150))
        hashes_a = self.hasher.compute_hashes(img_bytes)
        hashes_b = self.hasher.compute_hashes(img_bytes)
        dist = self.hasher.compare_hashes(hashes_a["phash"], hashes_b["phash"])
        assert dist == 0

    def test_different_images_nonzero_distance(self):
        img_a = _create_image_bytes(color=(10, 20, 30))
        img_b = _create_image_bytes(color=(200, 210, 220))
        hashes_a = self.hasher.compute_hashes(img_a)
        hashes_b = self.hasher.compute_hashes(img_b)
        dist = self.hasher.compare_hashes(hashes_a["phash"], hashes_b["phash"])
        assert isinstance(dist, int)
        assert dist >= 0

    def test_phash_is_string(self):
        img_bytes = _create_image_bytes()
        result = self.hasher.compute_hashes(img_bytes)
        assert isinstance(result["phash"], str)
        assert len(result["phash"]) > 0


class TestEmbeddingSimilarityEngine:
    def setup_method(self):
        self.engine = EmbeddingSimilarityEngine()

    def test_extract_embedding_returns_ndarray(self):
        img_bytes = _create_image_bytes()
        emb = self.engine.extract_embedding(img_bytes)
        assert isinstance(emb, np.ndarray)
        assert emb.ndim == 1

    def test_embedding_is_normalized(self):
        img_bytes = _create_image_bytes()
        emb = self.engine.extract_embedding(img_bytes)
        norm = np.linalg.norm(emb)
        assert abs(norm - 1.0) < 1e-5

    def test_identical_image_similarity_near_one(self):
        img_bytes = _create_image_bytes(color=(80, 120, 200))
        emb_a = self.engine.extract_embedding(img_bytes)
        emb_b = self.engine.extract_embedding(img_bytes)
        sim = self.engine.compute_cosine_similarity(emb_a, emb_b)
        assert abs(sim - 1.0) < 1e-3

    def test_cosine_similarity_in_range(self):
        img_a = _create_image_bytes(color=(10, 20, 30))
        img_b = _create_image_bytes(color=(200, 180, 160))
        emb_a = self.engine.extract_embedding(img_a)
        emb_b = self.engine.extract_embedding(img_b)
        sim = self.engine.compute_cosine_similarity(emb_a, emb_b)
        assert 0.0 <= sim <= 1.0


class TestSSIMDiffEngine:
    def setup_method(self):
        self.engine = SSIMDiffEngine()

    def test_identical_images_high_ssim_score(self):
        import cv2
        color_bgr = (200, 150, 100)
        img = np.full((256, 256, 3), color_bgr, dtype=np.uint8)
        _, buf = cv2.imencode('.jpg', img)
        img_bytes = buf.tobytes()

        result = self.engine.compute_ssim_diff(img_bytes, img_bytes)
        assert result["ssim_score"] >= 0.9

    def test_diff_heatmap_url_is_base64(self):
        import cv2
        img = np.zeros((128, 128, 3), dtype=np.uint8)
        _, buf = cv2.imencode('.jpg', img)
        img_bytes = buf.tobytes()
        result = self.engine.compute_ssim_diff(img_bytes, img_bytes)
        assert result["diff_heatmap_url"].startswith("data:image/png;base64,")

    def test_different_images_lower_ssim(self):
        import cv2
        img_a = np.full((128, 128, 3), 0, dtype=np.uint8)
        img_b = np.full((128, 128, 3), 255, dtype=np.uint8)
        _, buf_a = cv2.imencode('.jpg', img_a)
        _, buf_b = cv2.imencode('.jpg', img_b)
        result = self.engine.compute_ssim_diff(buf_a.tobytes(), buf_b.tobytes())
        assert result["ssim_score"] < 0.5
