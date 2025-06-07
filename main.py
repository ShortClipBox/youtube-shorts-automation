import time
import logging

from src.collection import run_collection
from src.processing import run_processing
from src.upload import run_upload
from src.analysis import run_analysis

# Basic logging setup
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def main_pipeline():
    """
    Main pipeline to run the YouTube Shorts automation process.
    """
    logging.info("--- Starting YouTube Shorts Automation Pipeline ---")

    try:
        # Step 1: Collect video metadata
        logging.info(">>> [PHASE 1/4] Starting video collection...")
        collection_success = run_collection()
        if not collection_success:
            logging.error("Video collection failed. Aborting pipeline.")
            return
        logging.info("<<< [PHASE 1/4] Video collection finished.")
        time.sleep(2)

        # Step 2: Process videos
        logging.info(">>> [PHASE 2/4] Starting video processing...")
        processing_success = run_processing()
        if not processing_success:
            logging.error("Video processing failed. Aborting pipeline.")
            return
        logging.info("<<< [PHASE 2/4] Video processing finished.")
        time.sleep(2)

        # Step 3: Upload videos
        logging.info(">>> [PHASE 3/4] Starting video upload...")
        upload_success = run_upload(processed_videos)
        if not upload_success:
            logging.error("Video upload failed. Aborting pipeline.")
            return
        logging.info("<<< [PHASE 3/4] Video upload finished.")
        time.sleep(2)

        # Step 4: Analyze performance
        logging.info(">>> [PHASE 4/4] Starting performance analysis...")
        analysis_success = run_analysis()
        if not analysis_success:
            logging.error("Performance analysis failed.")
        logging.info("<<< [PHASE 4/4] Performance analysis finished.")

    except Exception as e:
        logging.critical(f"An uncaught exception occurred in the main pipeline: {e}", exc_info=True)
    finally:
        logging.info("--- YouTube Shorts Automation Pipeline Finished ---")


if __name__ == "__main__":
    main_pipeline()
