import logging
import os

# config 모듈 임포트
import src.core.config as config

# Google Cloud Storage 임포트
from google.cloud import storage

# pytubefix 관련 임포트 및 경로 설정
import pytubefix
import pathlib
import time # time 모듈 임포트

# 로깅 설정
logging.basicConfig(
    level=logging.DEBUG,  # DEBUG 레벨로 변경
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(config.LOG_FILE),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import RedirectResponse
from google_auth_oauthlib.flow import Flow
from google.oauth2.credentials import Credentials
import os
import json
from src.collection import collect_videos
from src.processing.process import VideoProcessor
from src.analysis import run_analysis
from src.upload import run_upload
from src.core.youtube_api import YouTubeAPI

# FastAPI 애플리케이션 인스턴스 생성
app = FastAPI()

# GCS 버킷 이름 설정 (환경 변수에서 가져오거나 기본값 사용)
GCS_BUCKET_NAME = os.getenv("GCS_BUCKET_NAME", "shortclipbox-token-bucket")
TOKEN_FILE_NAME = "token.json"

# pytubefix 캐시 디렉터리 및 토큰 파일 설정
_pytubefix_cache_dir = pathlib.Path(pytubefix.__file__).parent.resolve() / '__cache__'
_pytubefix_token_file = os.path.join(_pytubefix_cache_dir, 'tokens.json')

# 미들웨어 추가: 모든 요청과 응답을 로깅
@app.middleware("http")
async def log_requests(request: Request, call_next):
    logger.debug(f"Request: {request.method} {request.url}")
    response = await call_next(request)
    logger.debug(f"Response: {response.status_code}")
    return response

# OAuth 2.0 클라이언트 설정
CLIENT_CONFIG = {
    "web": {
        "client_id": os.getenv("YOUTUBE_CLIENT_ID", "381688299677-r680d39d9as0g57rtpausib04b22rjje.apps.googleusercontent.com"),
        "client_secret": os.getenv("YOUTUBE_CLIENT_SECRET", "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"),
        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
        "token_uri": "https://oauth2.googleapis.com/token",
    }
}

SCOPES = [
    "https://www.googleapis.com/auth/youtube.readonly",
    "https://www.googleapis.com/auth/youtube.upload",
    "https://www.googleapis.com/auth/youtube"
]

# 인증 정보를 메모리에 저장 (GCS에서 로드된 임시 저장소 역할)
credentials_in_memory = None

print("🔥 FastAPI main.py가 실행되고 있습니다.")

@app.get("/")
async def read_root():
    return {"message": "서버가 정상적으로 실행 중입니다."}

@app.get("/auth/login")
async def login():
    """YouTube 로그인 페이지로 리다이렉트"""
    try:
        redirect_uri = os.getenv("REDIRECT_URI", "http://localhost:8000/auth/callback")
        flow = Flow.from_client_config(
            CLIENT_CONFIG,
            scopes=SCOPES,
            redirect_uri=redirect_uri
        )
        authorization_url, state = flow.authorization_url(
            access_type="offline",
            include_granted_scopes="true"
        )
        return RedirectResponse(authorization_url)
    except Exception as e:
        logger.error(f"Login error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/auth/callback")
async def auth_callback(code: str):
    """OAuth 인증 콜백 처리"""
    global credentials_in_memory
    try:
        redirect_uri = os.getenv("REDIRECT_URI", "http://localhost:8000/auth/callback")
        flow = Flow.from_client_config(
            CLIENT_CONFIG,
            scopes=SCOPES,
            redirect_uri=redirect_uri
        )
        flow.fetch_token(code=code)
        credentials = flow.credentials
        
        # GCS에 credentials 저장
        storage_client = storage.Client()
        bucket = storage_client.bucket(GCS_BUCKET_NAME)
        blob = bucket.blob(TOKEN_FILE_NAME)
        
        creds_dict = {
            "token": credentials.token,
            "refresh_token": credentials.refresh_token,
            "token_uri": credentials.token_uri,
            "client_id": credentials.client_id,
            "client_secret": credentials.client_secret,
            "scopes": credentials.scopes,
            "expiry": credentials.expiry.isoformat() if credentials.expiry else None
        }
        
        blob.upload_from_string(json.dumps(creds_dict))
        logger.info("인증 정보가 GCS에 성공적으로 저장되었습니다.")
        
        # 메모리에도 임시 저장
        credentials_in_memory = credentials

        # pytubefix 캐시도 업데이트
        visitor_data = os.getenv("YOUTUBE_VISITOR_DATA")
        po_token = os.getenv("YOUTUBE_PO_TOKEN")
        if visitor_data and po_token:
            save_pytubefix_tokens(credentials, visitor_data, po_token)
        else:
            logger.warning("YOUTUBE_VISITOR_DATA or YOUTUBE_PO_TOKEN environment variables are not set. pytubefix cache might not be fully populated.")

        return {"message": "인증이 완료되었습니다."}
    except Exception as e:
        logger.error(f"Callback error: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

async def get_youtube_credentials():
    """GCS에서 저장된 인증 정보를 가져오거나 갱신함"""
    global credentials_in_memory
    
    # 메모리에 인증 정보가 있으면 사용
    if credentials_in_memory and credentials_in_memory.valid:
        return credentials_in_memory

    try:
        storage_client = storage.Client()
        bucket = storage_client.bucket(GCS_BUCKET_NAME)
        blob = bucket.blob(TOKEN_FILE_NAME)
        
        # GCS에서 token.json 파일 읽기
        token_data = blob.download_as_string().decode("utf-8")
        creds_dict = json.loads(token_data)
        
        creds = Credentials.from_authorized_user_info(creds_dict, SCOPES)
        
        if not creds.valid:
            if creds.expired and creds.refresh_token:
                # Request 객체를 사용하지 않고 refresh
                creds.refresh(Request())
                # 갱신된 인증 정보 GCS에 저장
                updated_creds_dict = {
                    "token": creds.token,
                    "refresh_token": creds.refresh_token,
                    "token_uri": creds.token_uri,
                    "client_id": creds.client_id,
                    "client_secret": creds.client_secret,
                    "scopes": creds.scopes,
                    "expiry": creds.expiry.isoformat() if creds.expiry else None
                }
                blob.upload_from_string(json.dumps(updated_creds_dict))
                logger.info("갱신된 인증 정보가 GCS에 성공적으로 저장되었습니다.")
            else:
                logger.error("인증 정보가 만료되었고 갱신 토큰이 없습니다.")
                raise HTTPException(status_code=401, detail="인증이 만료되었습니다. /auth/login으로 이동해주세요.")

        # 메모리에 갱신된 인증 정보 저장
        credentials_in_memory = creds

        # pytubefix 캐시도 업데이트
        visitor_data = os.getenv("YOUTUBE_VISITOR_DATA")
        po_token = os.getenv("YOUTUBE_PO_TOKEN")
        if visitor_data and po_token:
            save_pytubefix_tokens(creds, visitor_data, po_token)
        else:
            logger.warning("YOUTUBE_VISITOR_DATA or YOUTUBE_PO_TOKEN environment variables are not set. pytubefix cache might not be fully populated.")

        return creds

    except Exception as e:
        logger.error(f"GCS에서 인증 정보를 로드하거나 갱신하는 중 오류 발생: {str(e)}", exc_info=True)
        raise HTTPException(status_code=401, detail="인증이 필요합니다. /auth/login으로 이동해주세요.")

@app.post("/run")
async def run_automation():
    try:
        logger.info("자동화 작업 시작")

        # 1. 비디오 수집
        logger.info("비디오 수집 시작")
        credentials = await get_youtube_credentials()
        collected_videos = collect_videos(credentials)
        logger.info(f"수집된 비디오: {len(collected_videos)}개")

        # 2. 비디오 처리
        logger.info("비디오 처리 시작")
        video_processor = VideoProcessor()
        processed_videos_count = video_processor.run_processing(collected_videos)
        logger.info(f"처리된 비디오: {processed_videos_count}개")

        # 3. 성과 분석
        logger.info("성과 분석 시작")
        analysis_results = run_analysis()
        logger.info("성과 분석 완료")

        # 4. YouTube 업로드
        logger.info("YouTube 업로드 시작")
        # run_upload 함수가 처리된 비디오 목록을 기대하는 경우:
        uploaded_videos = run_upload(video_processor.processed_videos, credentials)
        logger.info(f"업로드된 비디오: {len(uploaded_videos)}개")

        return {
            "status": "success",
            "collected_videos": len(collected_videos),
            "processed_videos": processed_videos_count,
            "uploaded_videos": len(uploaded_videos)
        }

    except Exception as e:
        logger.error(f"자동화 작업 중 오류 발생: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/status")
async def get_status():
    """현재 작업 상태 확인"""
    return {
        "status": "running",
        "message": "서버가 정상적으로 실행 중입니다."
    }

def run():
    # 3. Upload videos
    run_upload(uploaded_videos)

# pytubefix 토큰을 로컬 캐시에 저장하는 헬퍼 함수
def save_pytubefix_tokens(google_creds: Credentials, visitor_data: str, po_token: str):
    if not _pytubefix_cache_dir.exists():
        _pytubefix_cache_dir.mkdir(parents=True, exist_ok=True)

    data = {
        'access_token': google_creds.token,
        'refresh_token': google_creds.refresh_token,
        'expires': int(google_creds.expiry.timestamp()),
        'visitorData': visitor_data,
        'po_token': po_token
    }
    with open(_pytubefix_token_file, 'w') as f:
        json.dump(data, f)
    logger.info(f"pytubefix 토큰이 로컬 캐시 {_pytubefix_token_file}에 성공적으로 저장되었습니다.")

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8080))
    os.makedirs(os.path.dirname(config.LOG_FILE), exist_ok=True)
    uvicorn.run(app, host="0.0.0.0", port=port)