"""
YouTube Shorts Automation Package
"""

from .core import get_credentials, run_auth_flow, YouTubeAPI
from .collection import collect_videos
from .processing import run_processing
from .upload import run_upload
from .analysis import run_analysis

__version__ = "0.1.0"
__all__ = [
    'get_credentials',
    'run_auth_flow',
    'YouTubeAPI',
    'collect_videos',
    'run_processing',
    'run_upload',
    'run_analysis',
]
