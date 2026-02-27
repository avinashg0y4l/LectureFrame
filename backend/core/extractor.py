import cv2
import os
from skimage.metrics import structural_similarity as ssim

def extract_unique_frames(video_path: str, output_dir: str, threshold: float = 0.85, sampling_rate: int = 1) -> list:
    """
    Extracts unique frames from a video.
    Returns a list of dictionaries with frame path and timestamp.
    """
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    cap = cv2.VideoCapture(video_path)
    fps = cap.get(cv2.CAP_PROP_FPS)
    
    if fps == 0 or fps is None:
        fps = 30 # fallback
        
    frame_interval = int(fps * sampling_rate) # Check 1 frame per `sampling_rate` seconds
    
    count = 0
    saved_frames = []
    prev_frame_gray = None

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        if count % frame_interval == 0:
            # Resize frame to speed up SSIM calculation
            # standard 720p is fine, but SSIM on 720p can be slow, let's resize for comparison
            # Let's resize it to 640x360 just for comparison
            small_frame = cv2.resize(frame, (640, 360))
            gray = cv2.cvtColor(small_frame, cv2.COLOR_BGR2GRAY)
            
            is_unique = False
            if prev_frame_gray is None:
                is_unique = True
            else:
                score, _ = ssim(prev_frame_gray, gray, full=True)
                if score < threshold:  # Less similarity means it's a unique slide
                    is_unique = True

            if is_unique:
                timestamp_sec = count / fps
                minutes = int(timestamp_sec // 60)
                seconds = int(timestamp_sec % 60)
                timestamp_str = f"{minutes:02d}:{seconds:02d}"

                frame_filename = f"frame_{count}.jpg"
                frame_path = os.path.join(output_dir, frame_filename)
                
                # Adding timestamp on the original frame
                cv2.putText(frame, timestamp_str, (30, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 4, cv2.LINE_AA)
                cv2.putText(frame, timestamp_str, (30, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2, cv2.LINE_AA)
                
                cv2.imwrite(frame_path, frame)
                saved_frames.append({"path": frame_path, "timestamp": timestamp_str})
                prev_frame_gray = gray
                
        count += 1

    cap.release()
    return saved_frames
