import os
import json
import logging
import config
from src.core.youtube_api import YouTubeAPI

def run_upload():
    """
    Finds processed videos and uploads them to YouTube.
    """
    logging.info("Initializing video upload.")
    api = YouTubeAPI() # Use OAuth 2.0 for uploading
    if not api.youtube:
        logging.error("Failed to initialize YouTube API client. Aborting upload.")
        return False
        
    try:
        processed_videos = [f for f in os.listdir(config.PROCESSED_DIR) if f.endswith('.mp4')]
    except FileNotFoundError:
        logging.error(f"Processed directory not found: {config.PROCESSED_DIR}")
        return False

    if not processed_videos:
        logging.warning("No processed videos found to upload.")
        return True

    logging.info(f"Found {len(processed_videos)} videos to upload.")
    
    uploaded_video_log = []
    
    for video_file in processed_videos:
        file_path = os.path.join(config.PROCESSED_DIR, video_file)
        video_title = f"Cool Short - {os.path.splitext(video_file)[0]}" # Example title
        
        logging.info(f"Uploading {video_file}...")

        upload_result = api.upload_video(
            file_path=file_path,
            title=video_title,
            description=config.UPLOAD_DEFAULTS['description'],
            tags=config.UPLOAD_DEFAULTS['tags'],
            category_id=config.UPLOAD_DEFAULTS['categoryId'],
            privacy_status=config.UPLOAD_DEFAULTS['privacyStatus']
        )
        
        if upload_result and 'id' in upload_result:
            logging.info(f"Successfully uploaded '{video_title}' with ID: {upload_result['id']}")
            uploaded_video_log.append(upload_result)
        else:
            logging.error(f"Failed to upload {video_file}.")
            
    # Save log of uploaded videos
    try:
        with open(config.UPLOADED_VIDEOS_FILE, 'w', encoding='utf-8') as f:
            json.dump(uploaded_video_log, f, indent=4, ensure_ascii=False)
        logging.info(f"Upload log saved to {config.UPLOADED_VIDEOS_FILE}")
    except IOError as e:
        logging.error(f"Failed to write upload log: {e}")

    return True

if __name__ == '__main__':
    run_upload()
