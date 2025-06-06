import googleapiclient.discovery
import googleapiclient.errors

import config
import auth

class YouTubeAPI:
    """A wrapper class for the YouTube Data API v3."""

    def __init__(self, use_api_key=False):
        """
        Initializes the YouTube API client.
        :param use_api_key: If True, uses the API key for authentication (limited access).
                            If False, uses OAuth 2.0 credentials (full access).
        """
        self.youtube = None
        if use_api_key:
            try:
                self.youtube = googleapiclient.discovery.build(
                    "youtube", "v3", developerKey=config.YOUTUBE_API_KEY)
                print("YouTube API client initialized with API Key.")
            except Exception as e:
                print(f"Error initializing with API key: {e}")
        else:
            try:
                credentials = auth.get_credentials()
                self.youtube = googleapiclient.discovery.build(
                    "youtube", "v3", credentials=credentials)
                print("YouTube API client initialized with OAuth 2.0 credentials.")
            except Exception as e:
                print(f"Error initializing with OAuth credentials: {e}")

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
            request = self.youtube.videos().insert(
                part=",".join(body.keys()),
                body=body,
                media_body=file_path # In a real scenario, use MediaFileUpload
            )
            # This is a placeholder. Real upload requires MediaFileUpload from googleapiclient.http
            print(f"Placeholder: Would upload {file_path} with title '{title}'")
            # response = request.execute()
            # return response
            return {"id": "placeholder_video_id", "snippet": {"title": title}}
        except googleapiclient.errors.HttpError as e:
            print(f"An HTTP error {e.resp.status} occurred: {e.content}")
            return None
