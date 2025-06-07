import json
import logging
import os
import ssl
import certifi
from pytubefix import YouTube
from moviepy.editor import VideoFileClip
from src.core import config
from src.core import ffmpeg_utils
from datetime import datetime
# from typing import Tuple # Removed as dummy_po_token_verifier is no longer needed

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 핸들러가 없으면 추가
if not logger.handlers:
    handler = logging.StreamHandler()
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)

# Removed dummy verifiers as they interfere with pytubefix's token handling
# def dummy_oauth_verifier(verification_url: str, user_code: str):
#     logger.error(f"Attempted interactive OAuth verification in headless environment. This is not supported. Please ensure token.json is valid and accessible via GCS. Verification URL: {verification_url}, User Code: {user_code}")
#     raise Exception("Interactive OAuth verification attempted in headless environment.")

# def dummy_po_token_verifier() -> Tuple[str, str]:
#     visitor_data = os.getenv("YOUTUBE_VISITOR_DATA")
#     po_token = os.getenv("YOUTUBE_PO_TOKEN")
#     if not visitor_data or not po_token:
#         logger.error("YOUTUBE_VISITOR_DATA or YOUTUBE_PO_TOKEN environment variables are not set. Cannot proceed with PO Token verification.")
#         raise Exception("Missing YOUTUBE_VISITOR_DATA or YOUTUBE_PO_TOKEN environment variables for PO Token verification.")
#     logger.info("Using visitorData and po_token from environment variables for PO Token verification.")
#     return visitor_data, po_token

class VideoProcessor:
    def __init__(self):
        self.config = config
        self.processed_videos = []
        # SSL 컨텍스트 설정
        self.ssl_context = ssl.create_default_context(cafile=certifi.where())
        self.ssl_context.check_hostname = False
        self.ssl_context.verify_mode = ssl.CERT_NONE
        logger.info(f"SSL 컨텍스트 설정 완료: {certifi.where()}")
        
        # YouTube API 설정: 환경 변수에서 visitorData와 po_token을 읽어옵니다.
        # 이 값들은 https://github.com/YunzheZJU/youtube-po-token-generator와 같은 도구를 사용하여
        # YouTube 개발자 도구의 Network 탭에서 player 요청의 Payload에서 얻을 수 있습니다.
        self.visitor_data = os.getenv("YOUTUBE_VISITOR_DATA")
        self.po_token = os.getenv("YOUTUBE_PO_TOKEN")

    def run_processing(self, videos_data):
        """수집된 비디오를 처리하는 함수"""
        logger.info("비디오 처리 단계 시작")
        processed_count = 0
        
        if not isinstance(videos_data, list):
            logger.error(f"Invalid input for run_processing: Expected a list, got {type(videos_data)}")
            return 0

        for video in videos_data:
            try:
                logger.info(f"Processing video: {video.get('id')}")
                video_id = video.get('id')
                if not video_id:
                    logger.warning(f"Skipping video due to missing ID: {video}")
                    continue
                
                url = f"https://www.youtube.com/watch?v={video_id}"
                
                logger.info(f"YouTube 객체 생성 시도: {url}")
                yt = YouTube(
                    url,
                    use_oauth=True,
                    allow_oauth_cache=True
                    # Removed dummy verifiers: oauth_verifier=dummy_oauth_verifier, po_token_verifier=dummy_po_token_verifier
                )
                logger.info("YouTube 객체 생성 성공")
                
                logger.info(f"스트림 선택 시도 for {url}...")
                stream = yt.streams.filter(file_extension='mp4', progressive=True).order_by('resolution').desc().first()
                if not stream:
                    logger.warning(f"No suitable stream found for video: {url}. Skipping.")
                    continue
                logger.info(f"스트림 선택 성공: {stream.resolution} for {url}")
                
                logger.info(f"비디오 다운로드 시도: {url} to {self.config.DOWNLOADS_DIR}")
                output_path = stream.download(output_path=self.config.DOWNLOADS_DIR)
                logger.info(f"비디오 다운로드 완료: {output_path}")
                
                logger.info(f"Processing downloaded video: {output_path}")
                processed_path = self._process_video(output_path)
                
                if processed_path:
                    self.processed_videos.append({
                        'original_url': url,
                        'processed_path': processed_path,
                        'title': yt.title
                    })
                    processed_count += 1
                    logger.info(f"Successfully processed video: {url}")
                
            except Exception as e:
                logger.error(f"Error processing video {url}: {str(e)}", exc_info=True)
                continue
        
        logger.info(f"Video processing phase completed. Successfully processed {processed_count} videos.")
        return processed_count

    def _process_video(self, video_path):
        """비디오 처리"""
        try:
            processed_dir = self.config.PROCESSED_DIR
            os.makedirs(processed_dir, exist_ok=True)
            
            video_id = os.path.basename(video_path).split('.')[0]
            processed_path = os.path.join(processed_dir, f"{video_id}_short.mp4")
            
            logger.info(f"Loading video clip: {video_path}")
            video = VideoFileClip(video_path)
            
            if video.duration > self.config.SHORT_DURATION:
                video = video.subclip(0, self.config.SHORT_DURATION)
                logger.info(f"Video clipped to {self.config.SHORT_DURATION} seconds.")
            
            logger.info(f"Writing processed video to: {processed_path}")
            video.write_videofile(processed_path, codec='libx264', audio_codec='aac')
            video.close()
            
            logger.info(f"Original video removed: {video_path}")
            os.remove(video_path)
            
            return processed_path
        except Exception as e:
            logger.error(f"Error processing video {video_path}: {str(e)}", exc_info=True)
            return None
