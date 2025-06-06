import json
import logging
import os
import config
from src.core import ffmpeg_utils

def run_processing():
    """
    Loads the list of collected videos, "downloads" them,
    and "processes" them into Shorts format.
    """
    logging.info("Initializing video processing.")
    
    # Ensure output directories exist
    os.makedirs(config.DOWNLOADS_DIR, exist_ok=True)
    os.makedirs(config.PROCESSED_DIR, exist_ok=True)

    try:
        with open(config.VIDEO_LIST_FILE, 'r', encoding='utf-8') as f:
            videos_to_process = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        logging.error(f"Could not read or parse {config.VIDEO_LIST_FILE}: {e}")
        return False

    if not videos_to_process:
        logging.warning("Video list is empty. Nothing to process.")
        return True

    logging.info(f"Found {len(videos_to_process)} videos to process.")
    
    for video in videos_to_process:
        video_id = video.get('id', {}).get('videoId')
        video_title = video.get('snippet', {}).get('title', 'untitled')
        
        if not video_id:
            logging.warning(f"Skipping video with missing ID: {video_title}")
            continue

        logging.info(f"Processing video: {video_title} (ID: {video_id})")

        # --- Placeholder Steps ---
        # 1. Download video (placeholder)
        source_video_path = os.path.join(config.DOWNLOADS_DIR, f"{video_id}.mp4")
        logging.info(f"Placeholder: 'Downloading' video to {source_video_path}")
        # In a real implementation, you would use a library like pytube here.
        
        # 2. Process video using ffmpeg_utils (placeholder)
        processed_video_path = os.path.join(config.PROCESSED_DIR, f"{video_id}_short.mp4")
        ffmpeg_utils.change_aspect_ratio(source_video_path, processed_video_path, *config.OUTPUT_RESOLUTION)
        logging.info(f"Placeholder: 'Processed' video saved to {processed_video_path}")

    logging.info("Video processing phase completed.")
    return True

if __name__ == '__main__':
    run_processing()
