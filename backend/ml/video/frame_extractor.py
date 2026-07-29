import cv2
import tempfile
import os
from PIL import Image
import io
from ml.detection.detector import detector_service

class VideoAIDetector:
    """
    Video AI Frame-Sampling Orchestrator (F9).
    Samples video frames at 1 fps interval, evaluates each frame through the F1 detector,
    and aggregates an overall verdict + suspicion timeline.
    """

    def process_video_bytes(self, video_bytes: bytes, sample_fps: float = 1.0) -> dict:
        # Write bytes to temporary file for OpenCV reading
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as tmp:
            tmp.write(video_bytes)
            tmp_path = tmp.name

        try:
            cap = cv2.VideoCapture(tmp_path)
            fps = cap.get(cv2.CAP_PROP_FPS) or 30.0
            frame_interval = int(fps / sample_fps)
            if frame_interval <= 0:
                frame_interval = 1

            frame_count = 0
            analyzed_frames = []
            ai_scores = []

            while cap.isOpened():
                ret, frame = cap.read()
                if not ret:
                    break

                if frame_count % frame_interval == 0:
                    # Convert BGR OpenCV frame to JPEG bytes for detector
                    _, buffer = cv2.imencode('.jpg', frame)
                    frame_bytes = buffer.tobytes()

                    # Run inference on frame
                    result = detector_service.predict(frame_bytes)
                    timestamp = round(frame_count / fps, 2)
                    
                    frame_info = {
                        "timestamp_sec": timestamp,
                        "frame_index": frame_count,
                        "confidence": result["confidence"],
                        "is_ai": result["is_ai"]
                    }
                    analyzed_frames.append(frame_info)
                    ai_scores.append(result["confidence"])

                frame_count += 1
            
            cap.release()

            if not ai_scores:
                return {
                    "overall_verdict": "Unknown",
                    "overall_confidence": 0.0,
                    "frames_analyzed": 0,
                    "frame_timeline": []
                }

            avg_confidence = round(sum(ai_scores) / len(ai_scores), 2)
            is_overall_ai = avg_confidence >= 50.0
            verdict = "AI-Generated Video" if is_overall_ai else "Real Recorded Video"

            return {
                "overall_verdict": verdict,
                "overall_confidence": avg_confidence,
                "frames_analyzed": len(analyzed_frames),
                "frame_timeline": analyzed_frames
            }
        finally:
            if os.path.exists(tmp_path):
                os.remove(tmp_path)

video_service = VideoAIDetector()
