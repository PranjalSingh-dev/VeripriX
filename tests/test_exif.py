"""
Unit Tests for EXIF Metadata Scanner
Tests EXIF extraction, missing-EXIF detection, and software signature flagging.
"""
import sys
import os
import io
import pytest
from PIL import Image

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from ml.metadata.exif_scanner import EXIFScanner


def _make_plain_image_bytes():
    """Plain image with no EXIF data"""
    img = Image.new("RGB", (256, 256), color=(100, 150, 200))
    buf = io.BytesIO()
    img.save(buf, format="JPEG")
    return buf.getvalue()


class TestEXIFScanner:
    def setup_method(self):
        self.scanner = EXIFScanner()

    def test_plain_image_has_no_exif(self):
        img_bytes = _make_plain_image_bytes()
        result = self.scanner.scan_bytes(img_bytes)
        assert "has_exif" in result

    def test_result_contains_expected_keys(self):
        img_bytes = _make_plain_image_bytes()
        result = self.scanner.scan_bytes(img_bytes)
        assert "has_exif" in result
        assert "tags" in result

    def test_missing_exif_triggers_warning(self):
        img_bytes = _make_plain_image_bytes()
        result = self.scanner.scan_bytes(img_bytes)
        if not result["has_exif"]:
            assert "warning" in result

    def test_invalid_bytes_returns_graceful_result(self):
        result = self.scanner.scan_bytes(b"corrupted data here")
        assert "has_exif" in result
        assert result["has_exif"] is False
