import json
import logging
from ..core.youtube_api import YouTubeAPI
from ..core import config
import os
from typing import List, Dict

logger = logging.getLogger(__name__)

def collect_videos() -> List[Dict]:
    """
    YouTube Shorts 비디오를 수집하는 함수
    
    Returns:
        List[Dict]: 수집된 비디오 정보 리스트
    """
    try:
        # 임시로 테스트용 비디오 리스트 반환
        return [
            {
                "id": "test_video_1",
                "title": "Test Video 1",
                "url": "https://example.com/video1",
                "duration": 60
            },
            {
                "id": "test_video_2",
                "title": "Test Video 2",
                "url": "https://example.com/video2",
                "duration": 45
            }
        ]
    except Exception as e:
        logger.error(f"비디오 수집 중 오류 발생: {str(e)}")
        raise

if __name__ == '__main__':
    collect_videos()
