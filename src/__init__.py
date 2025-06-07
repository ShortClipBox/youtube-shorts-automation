"""
YouTube Shorts Automation Package
"""

from .core import get_credentials, YouTubeAPI
from .collection import collect_videos
from .processing import VideoProcessor
from .upload import run_upload
from .analysis import run_analysis

__version__ = "0.1.0"
__all__ = [
    'get_credentials',
    'YouTubeAPI',
    'collect_videos',
    'VideoProcessor',
    'run_upload',
    'run_analysis',
]
