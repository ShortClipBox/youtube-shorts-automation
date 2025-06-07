import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# --- API Keys & Authentication ---
# Get your API Key from Google Cloud Console
YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY", "YOUR_API_KEY_HERE")

# --- Search Configuration ---
# Keywords to search for on YouTube
SEARCH_KEYWORDS = ["interesting moments", "funny clips", "satisfying videos"]
MAX_RESULTS_PER_KEYWORD = 10

# --- Video Processing ---
# Target duration for each Short in seconds
SHORT_DURATION = 59
# Video resolution for output
OUTPUT_RESOLUTION = (1080, 1920) # (width, height)

# --- File & Directory Paths ---
# Base directory (project root)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Data paths
DATA_DIR = os.path.join(BASE_DIR, "data")
CLIENT_SECRETS_FILE = os.path.join(DATA_DIR, "client_secrets.json")
CREDENTIALS_FILE = os.path.join(DATA_DIR, "credentials.json")
VIDEO_LIST_FILE = os.path.join(DATA_DIR, "video_list.json")
UPLOADED_VIDEOS_FILE = os.path.join(DATA_DIR, "uploaded_videos.json")
ANALYTICS_REPORT_FILE = os.path.join(DATA_DIR, "analytics_report.csv")

# Output paths
OUTPUT_DIR = os.path.join(BASE_DIR, "output")
DOWNLOADS_DIR = os.path.join(OUTPUT_DIR, "downloads")
PROCESSED_DIR = os.path.join(OUTPUT_DIR, "processed")
THUMBNAILS_DIR = os.path.join(OUTPUT_DIR, "thumbnails")
ARCHIVE_DIR = os.path.join(OUTPUT_DIR, "archive")

# Asset paths
ASSETS_DIR = os.path.join(BASE_DIR, "assets")
INTRO_CLIP = os.path.join(ASSETS_DIR, "intro", "intro_clip.mp4")
OUTRO_CLIP = os.path.join(ASSETS_DIR, "outro", "outro_clip.mp4")
MUSIC_DIR = os.path.join(ASSETS_DIR, "music")
FONT_FILE = os.path.join(ASSETS_DIR, "fonts", "NanumGothicBold.ttf")

# Log path
LOGS_DIR = os.path.join(BASE_DIR, "logs")
LOG_FILE = os.path.join(LOGS_DIR, "app.log")

# --- YouTube Upload Settings ---
UPLOAD_DEFAULTS = {
    "categoryId": "24", # Entertainment
    "privacyStatus": "private", # 'private', 'public', or 'unlisted'
    "tags": ["shorts", "funny", "trending"],
    "description": "Check out this cool YouTube Short! #shorts"
}

# YouTube API 스코프 정의
SCOPES = [
    'https://www.googleapis.com/auth/youtube.upload',
    'https://www.googleapis.com/auth/youtube.readonly'
]

# YouTube API 설정
YOUTUBE_API_SERVICE_NAME = 'youtube'
YOUTUBE_API_VERSION = 'v3'
