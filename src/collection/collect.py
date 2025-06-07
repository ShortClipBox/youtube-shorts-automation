import json
import logging
from src.core.youtube_api import YouTubeAPI
from src.core import config
import os
from typing import List, Dict

logger = logging.getLogger(__name__)

# 비디오 수집
def collect_videos(credentials) -> List[Dict]:
    try:
        # YouTube API 클라이언트 초기화
        api = YouTubeAPI(credentials=credentials)
        if not api.youtube:
            logger.error("YouTube API 클라이언트 초기화 실패")
            return []

        # 검색 쿼리 설정
        search_query = "shorts"  # 실제 검색어로 수정 필요
        
        # 비디오 검색
        search_response = api.youtube.search().list(
            q=search_query,
            part="id,snippet",
            maxResults=10,
            type="video",
            videoDuration="short"
        ).execute()

        # 검색 결과 처리
        videos = []
        for item in search_response.get("items", []):
            video_id = item["id"]["videoId"]
            video_details = api.youtube.videos().list(
                part="snippet,contentDetails",
                id=video_id
            ).execute()

            if video_details["items"]:
                video_info = video_details["items"][0]
                videos.append({
                    "id": video_id,
                    "title": video_info["snippet"]["title"],
                    "description": video_info["snippet"]["description"],
                    "duration": video_info["contentDetails"]["duration"],
                    "publishedAt": video_info["snippet"]["publishedAt"]
                })

        logger.info(f"총 {len(videos)}개의 비디오를 수집했습니다.")

        # 수집된 비디오 정보를 파일로 저장
        os.makedirs(os.path.dirname(config.VIDEO_LIST_FILE), exist_ok=True)
        with open(config.VIDEO_LIST_FILE, 'w', encoding='utf-8') as f:
            json.dump(videos, f, indent=4)
        logger.info(f"수집된 비디오 목록을 {config.VIDEO_LIST_FILE}에 저장했습니다.")

        return videos

    except Exception as e:
        logger.error(f"비디오 수집 중 오류 발생: {str(e)}")
        return []

if __name__ == '__main__':
    collect_videos()
