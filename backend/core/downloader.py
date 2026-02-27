import os
import yt_dlp
import uuid

def download_video(url: str, output_dir: str) -> str:
    """
    Downloads a YouTube video to the specified directory.
    Returns the path to the downloaded video.
    """
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    video_id = str(uuid.uuid4())
    output_template = os.path.join(output_dir, f"{video_id}.%(ext)s")

    ydl_opts = {
        'format': 'best[ext=mp4][height<=720]/best[height<=720]/best',
        'outtmpl': output_template,
        'quiet': True,
        'no_warnings': True
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info_dict = ydl.extract_info(url, download=True)
        video_filename = ydl.prepare_filename(info_dict)
        # Handle cases where prepare_filename returns .webm instead of .mp4 (if merged)
        if not os.path.exists(video_filename):
            base, _ = os.path.splitext(video_filename)
            video_filename = f"{base}.mp4"

    return video_filename

def get_video_info(url: str):
    """
    Gets metadata of a video or playlist before downloading.
    """
    ydl_opts = {'quiet': True, 'extract_flat': True}
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)
        return info
