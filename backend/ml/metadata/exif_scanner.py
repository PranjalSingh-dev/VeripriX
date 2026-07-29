from PIL import Image
from PIL.ExifTags import TAGS
import io

class EXIFScanner:
    """
    EXIF Metadata & Forensic Scanner.
    Extracts camera attributes, timestamps, GPS tags, and identifies suspicious signals
    (e.g., missing EXIF tags common in AI generators or editing software signatures).
    """

    def scan_bytes(self, image_bytes: bytes) -> dict:
        try:
            image = Image.open(io.BytesIO(image_bytes))
            exif_raw = image._getexif()

            if not exif_raw:
                return {
                    "has_exif": False,
                    "warning": "Missing EXIF metadata (Typical for AI-generated images or stripped web assets)",
                    "tags": {}
                }

            parsed_tags = {}
            for tag_id, value in exif_raw.items():
                tag_name = TAGS.get(tag_id, tag_id)
                # Filter non-serializable objects
                if isinstance(value, (str, int, float)):
                    parsed_tags[str(tag_name)] = value

            software = parsed_tags.get("Software", "").lower()
            is_edited = any(tool in software for tool in ["photoshop", "gimp", "lightroom", "canva"])

            return {
                "has_exif": True,
                "camera_make": parsed_tags.get("Make", "Unknown"),
                "camera_model": parsed_tags.get("Model", "Unknown"),
                "date_taken": parsed_tags.get("DateTimeOriginal", "Unknown"),
                "software_signature": parsed_tags.get("Software", None),
                "is_edited_flag": is_edited,
                "tags": parsed_tags
            }
        except Exception as e:
            return {
                "has_exif": False,
                "warning": f"EXIF parsing error: {str(e)}",
                "tags": {}
            }

exif_service = EXIFScanner()
