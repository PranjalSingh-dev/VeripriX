import imagehash
from PIL import Image
import io

class PerceptualHasher:
    """
    Perceptual Hashing Engine.
    Uses pHash and dHash to quickly detect exact and near-duplicate images.
    """

    def compute_hashes(self, image_bytes: bytes) -> dict:
        image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
        phash = imagehash.phash(image)
        dhash = imagehash.dhash(image)
        return {
            "phash": str(phash),
            "dhash": str(dhash),
            "raw_phash": phash
        }

    def compare_hashes(self, hash_a: str, hash_b: str) -> int:
        ha = imagehash.hex_to_hash(hash_a)
        hb = imagehash.hex_to_hash(hash_b)
        return ha - hb  # Hamming distance

hasher_service = PerceptualHasher()
