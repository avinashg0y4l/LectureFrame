import os
from PIL import Image

def create_pdf_from_frames(frames: list, output_pdf_path: str):
    """
    Creates a PDF from a list of frame dictionaries.
    frames is a list of dicts: [{"path": "...", "timestamp": "..."}, ...]
    """
    if not frames:
        return None

    images = []
    first_image = None
    
    for frame in frames:
        frame_path = frame["path"]
        if os.path.exists(frame_path):
            # Load the image and ensure it's in RGB format for PDF
            img = Image.open(frame_path).convert('RGB')
            if first_image is None:
                first_image = img
            else:
                images.append(img)
                
    if first_image is not None:
        first_image.save(
            output_pdf_path,
            save_all=True,
            append_images=images,
            resolution=100.0,
            quality=85,
            format="PDF"
        )
        
    return output_pdf_path
