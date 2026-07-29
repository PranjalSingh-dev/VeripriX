import cv2
import numpy as np
from skimage.metrics import structural_similarity as ssim
import base64

class SSIMDiffEngine:
    """
    Structural Similarity (SSIM) Difference Engine.
    Generates a pixel-level difference heatmap revealing exact region modifications between two images.
    """

    def compute_ssim_diff(self, image_a_bytes: bytes, image_b_bytes: bytes) -> dict:
        img_a = cv2.imdecode(np.frombuffer(image_a_bytes, np.uint8), cv2.IMREAD_COLOR)
        img_b = cv2.imdecode(np.frombuffer(image_b_bytes, np.uint8), cv2.IMREAD_COLOR)

        if img_a is None or img_b is None:
            return {"score": 0.0, "diff_heatmap_url": None}

        # Resize image B to match image A dimensions for SSIM evaluation
        h, w, _ = img_a.shape
        img_b_resized = cv2.resize(img_b, (w, h))

        gray_a = cv2.cvtColor(img_a, cv2.COLOR_BGR2GRAY)
        gray_b = cv2.cvtColor(img_b_resized, cv2.COLOR_BGR2GRAY)

        score, diff = ssim(gray_a, gray_b, full=True)
        diff = (diff * 255).astype("uint8")

        # Colorize difference map
        diff_heatmap = cv2.applyColorMap(255 - diff, cv2.COLORMAP_JET)
        
        _, buffer = cv2.imencode('.png', diff_heatmap)
        encoded_string = base64.b64encode(buffer).decode('utf-8')
        diff_url = f"data:image/png;base64,{encoded_string}"

        return {
            "ssim_score": round(float(score), 4),
            "diff_heatmap_url": diff_url
        }

ssim_service = SSIMDiffEngine()
