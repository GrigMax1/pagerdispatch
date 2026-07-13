from datetime import datetime
import pytz
from config import Config
from typing import Optional

config = Config()

class TimeHelper:
    """Helper functions for time operations."""
    
    @staticmethod
    def get_current_time() -> datetime:
        """Get current time in configured timezone."""
        tz = pytz.timezone(config.timezone)
        return datetime.now(tz)
    
    @staticmethod
    def format_time(dt: Optional[datetime] = None) -> str:
        """Format datetime for display."""
        if dt is None:
            dt = TimeHelper.get_current_time()
        return dt.strftime('%H:%M')
    
    @staticmethod
    def format_full_datetime(dt: Optional[datetime] = None) -> str:
        """Format datetime with date and time."""
        if dt is None:
            dt = TimeHelper.get_current_time()
        return dt.strftime('%Y-%m-%d %H:%M:%S')


class DispatchCategories:
    """Dispatch category definitions."""
    
    CATEGORIES = {
        'emergency': {
            'name': 'Emergency',
            'emoji': '🚨',
            'description': 'Life-threatening situations requiring immediate response'
        },
        'operation': {
            'name': 'Police Operation',
            'emoji': '🎯',
            'description': 'Planned police operations and raids'
        },
        'traffic': {
            'name': 'Traffic Enforcement',
            'emoji': '🚧',
            'description': 'Traffic stops, DUI checkpoints, enforcement'
        },
        'training': {
            'name': 'Training',
            'emoji': '🎓',
            'description': 'Training exercises and drills'
        },
        'announcement': {
            'name': 'General Announcement',
            'emoji': '📢',
            'description': 'Department announcements and notifications'
        }
    }
    
    @classmethod
    def get_select_options(cls):
        """Get Discord select menu options for categories."""
        import discord
        options = []
        for key, data in cls.CATEGORIES.items():
            options.append(
                discord.SelectOption(
                    label=data['name'],
                    value=key,
                    emoji=data['emoji'],
                    description=data['description']
                )
            )
        return options
    
    @classmethod
    def get_category_data(cls, category_key: str):
        """Get category data by key."""
        return cls.CATEGORIES.get(category_key, {})


class DispatchStatuses:
    """Dispatch status constants."""
    ACTIVE = 'Active'
    CLOSED = 'Closed'
    
    # Officer response statuses
    RESPONDING = 'Responding'
    EN_ROUTE = 'En Route'
    ON_SCENE = 'On Scene'
    TAKING_COMMAND = 'Taking Command'
    UNABLE = 'Unable'


class LogActions:
    """Log action constants."""
    DISPATCH_CREATED = 'Dispatch Created'
    DISPATCH_CLOSED = 'Dispatch Closed'
    PANIC_ALARM = 'Panic Alarm Activated'
    OFFICER_RESPONDING = 'Officer Responding'
    OFFICER_EN_ROUTE = 'Officer En Route'
    OFFICER_ON_SCENE = 'Officer On Scene'
    OFFICER_TAKING_COMMAND = 'Officer Taking Command'
    OFFICER_UNABLE = 'Officer Unable'
    UNIT_SELECTION_CHANGED = 'Unit Selection Changed'
