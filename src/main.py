from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import RedirectResponse
from google_auth_oauthlib.flow import Flow
from google.oauth2.credentials import Credentials
import os
import json
from src.collection import collect_videos
from src.processing import run_processing
from src.analysis import run_analysis
from src.upload import run_upload
import logging

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

# OAuth 2.0 클라이언트 설정
CLIENT_CONFIG = {
    "web": {
        "client_id": os.getenv("YOUTUBE_CLIENT_ID"),
        "client_secret": os.getenv("YOUTUBE_CLIENT_SECRET"),
        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
        "token_uri": "https://oauth2.googleapis.com/token",
        "redirect_uris": [os.getenv("YOUTUBE_REDIRECT_URI")],
    }
}

SCOPES = [
    "https://www.googleapis.com/auth/youtube.upload",
    "https://www.googleapis.com/auth/youtube"
]

@app.get("/")
async def root():
    return {"message": "YouTube Shorts Automation API is running"}

@app.get("/auth/login")
async def login():
    """YouTube 로그인 페이지로 리다이렉트"""
    try:
        flow = Flow.from_client_config(
            CLIENT_CONFIG,
            scopes=SCOPES,
            redirect_uri=os.getenv("YOUTUBE_REDIRECT_URI")
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
    try:
        flow = Flow.from_client_config(
            CLIENT_CONFIG,
            scopes=SCOPES,
            redirect_uri=os.getenv("YOUTUBE_REDIRECT_URI")
        )
        flow.fetch_token(code=code)
        credentials = flow.credentials
        
        # credentials를 JSON으로 저장
        creds_dict = {
            "token": credentials.token,
            "refresh_token": credentials.refresh_token,
            "token_uri": credentials.token_uri,
            "client_id": credentials.client_id,
            "client_secret": credentials.client_secret,
            "scopes": credentials.scopes
        }
        
        with open("credentials.json", "w") as f:
            json.dump(creds_dict, f)
            
        return {"message": "인증이 완료되었습니다. 이제 자동화를 시작할 수 있습니다."}
    except Exception as e:
        logger.error(f"Callback error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/run")
async def run_automation_task():
    """전체 자동화 프로세스 실행"""
    try:
        # 1. 비디오 수집
        logger.info("비디오 수집 시작")
        collected_videos = collect_videos()
        logger.info(f"수집된 비디오: {len(collected_videos)}개")
        
        # 2. 비디오 처리
        logger.info("비디오 처리 시작")
        processed_videos = run_processing()
        logger.info(f"처리된 비디오: {len(processed_videos)}개")
        
        # 3. 성과 분석
        logger.info("성과 분석 시작")
        analysis_results = run_analysis()
        logger.info("성과 분석 완료")
        
        # 4. YouTube 업로드
        logger.info("YouTube 업로드 시작")
        # credentials.json 파일에서 인증 정보 로드
        with open("credentials.json", "r") as f:
            creds_dict = json.load(f)
            credentials = Credentials(
                token=creds_dict["token"],
                refresh_token=creds_dict["refresh_token"],
                token_uri=creds_dict["token_uri"],
                client_id=creds_dict["client_id"],
                client_secret=creds_dict["client_secret"],
                scopes=creds_dict["scopes"]
            )
        
        upload_results = run_upload(processed_videos, credentials)
        logger.info(f"업로드된 비디오: {len(upload_results)}개")
        
        return {
            "status": "success",
            "collected_videos": len(collected_videos),
            "processed_videos": len(processed_videos),
            "uploaded_videos": len(upload_results)
        }
    except Exception as e:
        logger.error(f"자동화 작업 중 오류 발생: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/status")
async def get_status():
    """현재 작업 상태 확인"""
    return {
        "status": "running",
        "message": "서버가 정상적으로 실행 중입니다."
    } 