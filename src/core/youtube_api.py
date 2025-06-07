import googleapiclient.discovery
import googleapiclient.errors
from googleapiclient.http import MediaFileUpload

# from . import auth # auth 모듈의 직접적인 의존성을 제거합니다.
from . import config

class YouTubeAPI:
    """A wrapper class for the YouTube Data API v3."""

    def __init__(self, credentials=None, developerKey=None):
        """
        Initializes the YouTube API client.
        :param credentials: OAuth 2.0 credentials object.
        :param developerKey: YouTube Data API Key.
        """
        self.youtube = None
        if credentials:
            try:
                self.youtube = googleapiclient.discovery.build(
                    "youtube", "v3", credentials=credentials)
                print("YouTube API client initialized with OAuth 2.0 credentials.")
            except Exception as e:
                print(f"Error initializing with OAuth credentials: {e}")
        elif developerKey:
            try:
                self.youtube = googleapiclient.discovery.build(
                    "youtube", "v3", developerKey=developerKey)
                print("YouTube API client initialized with API Key.")
            except Exception as e:
                print(f"Error initializing with API key: {e}")
        else:
            print("Warning: YouTubeAPI initialized without credentials or API key.")

    def search_videos(self, query, max_results=5):
        """
        Searches for videos on YouTube.
        :param query: The search term.
        :param max_results: The maximum number of results to return.
        :return: A list of search results.
        """
        if not self.youtube:
            print("YouTube client not initialized.")
            return []

        try:
            request = self.youtube.search().list(
                q=query,
                part="snippet",
                type="video",
                maxResults=max_results
            )
            response = request.execute()
            return response.get("items", [])
        except googleapiclient.errors.HttpError as e:
            print(f"An HTTP error {e.resp.status} occurred: {e.content}")
            return []

    def get_video_details(self, video_id):
        """
        Fetches details for a specific video.
        :param video_id: The ID of the video.
        :return: A dictionary containing video details.
        """
        if not self.youtube:
            print("YouTube client not initialized.")
            return None

        try:
            request = self.youtube.videos().list(
                part="snippet,statistics,contentDetails",
                id=video_id
            )
            response = request.execute()
            return response.get("items", [None])[0]
        except googleapiclient.errors.HttpError as e:
            print(f"An HTTP error {e.resp.status} occurred: {e.content}")
            return None

    def upload_video(self, file_path, title, description, tags, category_id, privacy_status):
        """
        Uploads a video to YouTube.
        :param file_path: Path to the video file.
        :return: The upload response from YouTube.
        """
        if not self.youtube:
            print("YouTube client not initialized.")
            return None

        try:
            body = {
                "snippet": {
                    "title": title,
                    "description": description,
                    "tags": tags,
                    "categoryId": category_id
                },
                "status": {
                    "privacyStatus": privacy_status
                }
            }
            media_body = MediaFileUpload(file_path, resumable=True)
            request = self.youtube.videos().insert(
                part=",".join(body.keys()),
                body=body,
                media_body=media_body
            )
            response = request.execute()
            print(f"Successfully uploaded '{title}' with ID: {response['id']}")
            return {"id": response['id'], "snippet": {"title": title}}
        except googleapiclient.errors.HttpError as e:
            print(f"An HTTP error {e.resp.status} occurred: {e.content}")
            return None
