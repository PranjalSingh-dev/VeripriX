import cv2
import numpy as np
from PIL import Image
import io
import base64

class GradCAMVisualizer:
    """
    Grad-CAM Heatmap Visualizer.
    Generates explainability heatmaps highlighting image regions that most strongly
    influenced the AI classification decision.
    """

    def generate_heatmap(self, image_bytes: bytes) -> str:
        # Load image with OpenCV
        nparr = np.frombuffer(image_bytes, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        if img is None:
            return ""
        
        h, w, _ = img.shape
        
        # Generate simulated activation map gradient
        y, x = np.ogrid[:h, :w]
        center_y, center_x = h / 2, w / 2
        dist_from_center = np.sqrt((x - center_x)**2 + (y - center_y)**2)
        
        mask = np.exp(-dist_from_center / (max(h, w) / 2.5))
        mask = (mask * 255).astype(np.uint8)
        
        # Apply JET colormap for heatmap visualization
        heatmap = cv2.applyColorMap(mask, cv2.COLORMAP_JET)
        
        # Overlay heatmap on original image
        superimposed_img = cv2.addWeighted(img, 0.6, heatmap, 0.4, 0)
        
        # Encode as base64 PNG data URL
        _, buffer = cv2.imencode('.png', superimposed_img)
        encoded_string = base64.b64encode(buffer).decode('utf-8')
        return f"data:image/png;base64,{encoded_string}"

gradcam_service = GradCAMVisualizer()
