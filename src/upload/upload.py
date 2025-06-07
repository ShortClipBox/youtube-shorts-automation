import os
import json
import logging
import time
from datetime import datetime, timedelta
from ..core import config
from ..core.youtube_api import YouTubeAPI
# from google.oauth2.credentials import Credentials # 더 이상 필요 없음

# 하루 최대 업로드 수 제한
MAX_DAILY_UPLOADS = 5
# 업로드 간격 (초)
UPLOAD_INTERVAL = 60

def get_today_uploads():
    """오늘 업로드된 비디오 수를 반환합니다."""
    try:
        with open(config.UPLOADED_VIDEOS_FILE, 'r', encoding='utf-8') as f:
            uploaded_videos = json.load(f)
            today = datetime.now().date()
            today_uploads = sum(1 for video in uploaded_videos 
                              if datetime.fromisoformat(video.get('uploaded_at', '')).date() == today)
            return today_uploads
    except (FileNotFoundError, json.JSONDecodeError):
        return 0

def run_upload(processed_videos: list, credentials):
    """
    Finds processed videos and uploads them to YouTube.
    """
    logging.info("Initializing video upload.")
    
    # 전달받은 credentials 객체로 YouTubeAPI 초기화
    api = YouTubeAPI(credentials=credentials)
    
    if not api.youtube:
        logging.error("Failed to initialize YouTube API client. Aborting upload.")
        return []
        
    if not processed_videos:
        logging.warning("No processed videos found to upload.")
        return []

    # 오늘의 업로드 수 확인
    today_uploads = get_today_uploads()
    if today_uploads >= MAX_DAILY_UPLOADS:
        logging.warning(f"Daily upload limit ({MAX_DAILY_UPLOADS}) reached. Skipping uploads.")
        return []

    logging.info(f"Found {len(processed_videos)} videos to upload.")
    
    uploaded_video_log = []
    
    for video_info in processed_videos:
        # 일일 업로드 제한 확인
        if today_uploads >= MAX_DAILY_UPLOADS:
            logging.warning(f"Daily upload limit ({MAX_DAILY_UPLOADS}) reached. Stopping uploads.")
            break

        file_path = video_info.get('processed_path')
        video_title = video_info.get('title', f"Cool Short - {os.path.splitext(os.path.basename(file_path))[0] if file_path else 'untitled'}")
        
        if not file_path or not os.path.exists(file_path):
            logging.warning(f"Processed video file not found or path is invalid: {file_path}. Skipping upload.")
            continue
             
        logging.info(f"Uploading {os.path.basename(file_path)}...")

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
            # 업로드 시간 추가
            upload_result['uploaded_at'] = datetime.now().isoformat()
            uploaded_video_log.append(upload_result)
            today_uploads += 1
            
            # 업로드 간격 대기
            if today_uploads < MAX_DAILY_UPLOADS:
                logging.info(f"Waiting {UPLOAD_INTERVAL} seconds before next upload...")
                time.sleep(UPLOAD_INTERVAL)
        else:
            logging.error(f"Failed to upload {os.path.basename(file_path)}.")
            
    # Save log of uploaded videos
    try:
        os.makedirs(os.path.dirname(config.UPLOADED_VIDEOS_FILE), exist_ok=True)
        with open(config.UPLOADED_VIDEOS_FILE, 'w', encoding='utf-8') as f:
            json.dump(uploaded_video_log, f, indent=4)
        logging.info(f"Upload process finished. {len(uploaded_video_log)} videos uploaded.")
    except IOError as e:
        logging.error(f"Failed to process upload results: {e}")

    return uploaded_video_log

if __name__ == '__main__':
    # 로컬 테스트 시 필요한 경우 여기에 인자 전달 로직 추가
    # 예: run_upload(['path/to/video.mp4'])
    pass
