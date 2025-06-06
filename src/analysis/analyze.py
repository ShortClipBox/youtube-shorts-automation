import csv
import json
import logging
from ..core import config
from ..core.youtube_api import YouTubeAPI

def run_analysis():
    """
    Analyzes the performance of uploaded videos and generates a CSV report.
    """
    logging.info("Initializing performance analysis.")
    api = YouTubeAPI() # Use OAuth 2.0 for reading stats
    if not api.youtube:
        logging.error("Failed to initialize YouTube API client. Aborting analysis.")
        return False
        
    try:
        with open(config.UPLOADED_VIDEOS_FILE, 'r', encoding='utf-8') as f:
            uploaded_videos = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        logging.warning("No uploaded videos log found. Nothing to analyze.")
        return True
        
    if not uploaded_videos:
        logging.warning("Uploaded videos log is empty. Nothing to analyze.")
        return True
        
    video_ids = [video['id'] for video in uploaded_videos if 'id' in video]
    if not video_ids:
        logging.warning("No video IDs found in the log.")
        return True

    logging.info(f"Fetching statistics for {len(video_ids)} videos.")
    
    report_data = []
    
    # YouTube API allows fetching details for multiple video IDs at once
    # For this placeholder, we'll iterate
    for video_id in video_ids:
        details = api.get_video_details(video_id)
        if details:
            snippet = details.get('snippet', {})
            stats = details.get('statistics', {})
            report_row = {
                'VideoID': video_id,
                'Title': snippet.get('title', 'N/A'),
                'UploadDate': snippet.get('publishedAt', 'N/A'),
                'Views': stats.get('viewCount', 0),
                'Likes': stats.get('likeCount', 0)
            }
            report_data.append(report_row)
        else:
            logging.warning(f"Could not fetch details for video ID: {video_id}")
            
    # Write report to CSV
    if not report_data:
        logging.warning("No data collected for the report.")
        return True
        
    try:
        with open(config.ANALYTICS_REPORT_FILE, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=['VideoID', 'Title', 'UploadDate', 'Views', 'Likes'])
            writer.writeheader()
            writer.writerows(report_data)
        logging.info(f"Analytics report successfully saved to {config.ANALYTICS_REPORT_FILE}")
    except IOError as e:
        logging.error(f"Failed to write analytics report: {e}")
        return False
        
    return True

if __name__ == '__main__':
    run_analysis()
