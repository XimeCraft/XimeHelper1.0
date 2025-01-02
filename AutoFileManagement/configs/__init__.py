"""
AutoFileManagement configs package initialization
Exports configuration managers for the application and its modules
"""

from .config import AutoFileManagementConfig
from .AutoFileOpening import AutoFileOpeningConfig

__all__ = [
    'AutoFileManagementConfig',
    'AutoFileOpeningConfig'
] 