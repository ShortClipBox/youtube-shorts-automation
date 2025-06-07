import os
import sys
from pathlib import Path

# 프로젝트 루트 경로를 PYTHONPATH에 추가
project_root = str(Path(__file__).parent.parent.parent)
if project_root not in sys.path:
    sys.path.append(project_root)

from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from src.core import config

# The scopes required for the YouTube Data API
SCOPES = ['https://www.googleapis.com/auth/youtube.upload', 'https://www.googleapis.com/auth/youtube.readonly']

def get_credentials():
    creds = None
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', config.SCOPES)
    
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_config(
                {
                    "installed": {
                        "client_id": os.getenv("YOUTUBE_CLIENT_ID"),
                        "client_secret": os.getenv("YOUTUBE_CLIENT_SECRET"),
                        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                        "token_uri": "https://oauth2.googleapis.com/token",
                        "redirect_uris": [os.getenv("REDIRECT_URI", "http://localhost")]
                    }
                },
                config.SCOPES
            )
            creds = flow.run_local_server(port=0)
        
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    
    return creds

if __name__ == '__main__':
    creds = get_credentials()
    print("인증이 완료되었습니다!")
    print(f"리프레시 토큰: {creds.refresh_token}")
