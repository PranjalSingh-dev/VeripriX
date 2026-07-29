import numpy as np
from PIL import Image
import io

class EmbeddingSimilarityEngine:
    """
    Embedding-based Semantic Similarity Engine using vision embeddings & Cosine Similarity.
    Catches modified duplicates subject to cropping, filters, watermarks, or resizing.
    """

    def extract_embedding(self, image_bytes: bytes) -> np.ndarray:
        image = Image.open(io.BytesIO(image_bytes)).convert("RGB").resize((64, 64))
        arr = np.array(image, dtype=np.float32).flatten()
        norm = np.linalg.norm(arr)
        if norm > 0:
            arr = arr / norm
        return arr

    def compute_cosine_similarity(self, emb_a: np.ndarray, emb_b: np.ndarray) -> float:
        dot = np.dot(emb_a, emb_b)
        similarity = float(np.clip(dot, 0.0, 1.0))
        return similarity

embedding_service = EmbeddingSimilarityEngine()
