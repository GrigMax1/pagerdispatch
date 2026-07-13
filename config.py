import json
import os
from typing import Optional
from dotenv import load_dotenv

load_dotenv()

class Config:
    """Centralized configuration loader."""
    
    _instance: Optional['Config'] = None
    _config: dict = {}
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Config, cls).__new__(cls)
            cls._instance._load_config()
        return cls._instance
    
    def _load_config(self) -> None:
        """Load configuration from config.json and environment variables."""
        config_path = os.path.join(os.path.dirname(__file__), 'config.json')
        
        try:
            with open(config_path, 'r') as f:
                self._config = json.load(f)
        except FileNotFoundError:
            raise FileNotFoundError(
                f"config.json not found at {config_path}. "
                "Please copy config.json.example to config.json and configure it."
            )
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON in config.json: {e}")
    
    def get(self, key: str, default=None):
        """Get a configuration value."""
        return self._config.get(key, default)
    
    def get_token(self) -> str:
        """Get the Discord bot token from environment."""
        token = os.getenv('DISCORD_TOKEN')
        if not token:
            raise ValueError(
                "DISCORD_TOKEN not found in .env file. "
                "Please create .env file with your bot token."
            )
        return token
    
    @property
    def guild_id(self) -> int:
        return self.get('guild_id', 0)
    
    @property
    def dispatch_channel_id(self) -> int:
        return self.get('dispatch_channel_id', 0)
    
    @property
    def dispatch_console_channel_id(self) -> int:
        return self.get('dispatch_console_channel_id', 0)
    
    @property
    def log_channel_id(self) -> int:
        return self.get('log_channel_id', 0)
    
    @property
    def police_role_id(self) -> int:
        return self.get('police_role_id', 0)
    
    @property
    def swat_role_id(self) -> int:
        return self.get('swat_role_id', 0)
    
    @property
    def detective_role_id(self) -> int:
        return self.get('detective_role_id', 0)
    
    @property
    def traffic_role_id(self) -> int:
        return self.get('traffic_role_id', 0)
    
    @property
    def supervisor_role_ids(self) -> list[int]:
        return self.get('supervisor_role_ids', [])
    
    @property
    def department_logo_url(self) -> str:
        return self.get('department_logo_url', '')
    
    @property
    def embed_color(self) -> int:
        return self.get('embed_color', 15158332)
    
    @property
    def footer_text(self) -> str:
        return self.get('footer_text', 'SAPD Dispatch System')
    
    @property
    def timezone(self) -> str:
        return self.get('timezone', 'America/Los_Angeles')
