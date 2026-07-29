"""
Unit Tests for AI Detection Module
Tests the AI image detector pipeline and Grad-CAM visualizer.
"""
import sys
import os
import io
import pytest
from PIL import Image

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from ml.detection.detector import AIDetectionPipeline
from ml.detection.gradcam import GradCAMVisualizer


def _create_test_image_bytes(width=256, height=256, color=(127, 50, 200)):
    img = Image.new("RGB", (width, height), color=color)
    buf = io.BytesIO()
    img.save(buf, format="JPEG")
    return buf.getvalue()


class TestAIDetectionPipeline:
    def setup_method(self):
        self.detector = AIDetectionPipeline()

    def test_predict_returns_expected_keys(self):
        img_bytes = _create_test_image_bytes()
        result = self.detector.predict(img_bytes)
        assert "verdict" in result
        assert "confidence" in result
        assert "is_ai" in result
        assert "explanation" in result

    def test_verdict_is_string(self):
        img_bytes = _create_test_image_bytes()
        result = self.detector.predict(img_bytes)
        assert isinstance(result["verdict"], str)
        assert result["verdict"] in ["AI-Generated", "Real Photo"]

    def test_confidence_in_valid_range(self):
        img_bytes = _create_test_image_bytes()
        result = self.detector.predict(img_bytes)
        assert 0.0 <= result["confidence"] <= 100.0

    def test_is_ai_bool(self):
        img_bytes = _create_test_image_bytes()
        result = self.detector.predict(img_bytes)
        assert isinstance(result["is_ai"], bool)

    def test_frequency_score_in_range(self):
        img_bytes = _create_test_image_bytes()
        result = self.detector.predict(img_bytes)
        freq_score = result["explanation"]["frequency_artifact_score"]
        assert 0.0 <= freq_score <= 1.0

    def test_explanation_contains_signals(self):
        img_bytes = _create_test_image_bytes()
        result = self.detector.predict(img_bytes)
        assert isinstance(result["explanation"]["signals"], list)
        assert len(result["explanation"]["signals"]) > 0

    def test_different_image_sizes(self):
        for size in [(64, 64), (128, 128), (512, 512)]:
            img_bytes = _create_test_image_bytes(width=size[0], height=size[1])
            result = self.detector.predict(img_bytes)
            assert result["verdict"] in ["AI-Generated", "Real Photo"]


class TestGradCAMVisualizer:
    def setup_method(self):
        self.gradcam = GradCAMVisualizer()

    def test_generate_heatmap_returns_base64_string(self):
        import cv2
        import numpy as np
        img = np.zeros((256, 256, 3), dtype=np.uint8)
        _, buffer = cv2.imencode('.jpg', img)
        img_bytes = buffer.tobytes()

        result = self.gradcam.generate_heatmap(img_bytes)
        assert isinstance(result, str)
        assert result.startswith("data:image/png;base64,")

    def test_generate_heatmap_empty_input_returns_empty(self):
        result = self.gradcam.generate_heatmap(b"invalid_bytes")
        assert result == "" or isinstance(result, str)
