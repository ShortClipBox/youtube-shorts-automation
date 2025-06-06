import json
import logging
import config
from src.core.youtube_api import YouTubeAPI

def run_collection():
    """
    Uses the YouTubeAPI to search for videos based on keywords
    and saves the metadata to a JSON file.
    """
    logging.info("Initializing video collection.")
    api = YouTubeAPI(use_api_key=True) # Use API key for searching
    
    if not api.youtube:
        logging.error("Failed to initialize YouTube API client. Aborting collection.")
        return False

    all_videos = []
    for keyword in config.SEARCH_KEYWORDS:
        logging.info(f"Searching for videos with keyword: '{keyword}'")
        try:
            videos = api.search_videos(keyword, max_results=config.MAX_RESULTS_PER_KEYWORD)
            if videos:
                all_videos.extend(videos)
                logging.info(f"Found {len(videos)} videos for '{keyword}'.")
            else:
                logging.warning(f"No videos found for '{keyword}'.")
        except Exception as e:
            logging.error(f"An error occurred while searching for '{keyword}': {e}")
            continue

    if not all_videos:
        logging.warning("No videos were collected.")
        return False
        
    try:
        with open(config.VIDEO_LIST_FILE, 'w', encoding='utf-8') as f:
            json.dump(all_videos, f, indent=4, ensure_ascii=False)
        logging.info(f"Successfully saved {len(all_videos)} video metadata entries to {config.VIDEO_LIST_FILE}")
    except IOError as e:
        logging.error(f"Failed to write to file {config.VIDEO_LIST_FILE}: {e}")
        return False

    return True

if __name__ == '__main__':
    run_collection()
