"""
Configuration Management

Handles all configuration for the Gemini Legion backend.
"""

from pydantic_settings import BaseSettings
from pydantic import Field, model_validator # Added model_validator
from typing import Optional, List, Dict, Any # Added Any
import os
from pathlib import Path

# Determine base_dir once at the module level
_BASE_DIR = Path(__file__).resolve().parent.parent


class Settings(BaseSettings):
    """Application settings with environment variable support"""
    
    # Application
    app_name: str = "Gemini Legion Backend"
    app_version: str = "0.1.0"
    debug: bool = Field(default=False, env="DEBUG")
    
    # Server
    host: str = Field(default="0.0.0.0", env="HOST")
    port: int = Field(default=8000, env="PORT")
    reload: bool = Field(default=True, env="RELOAD")
    
    # CORS
    cors_origins: List[str] = Field(
        default=["http://localhost:3000", "http://localhost:5173"],
        env="CORS_ORIGINS"
    )
    
    # Database
    database_url: str = Field(
        default="sqlite+aiosqlite:///./gemini_legion.db",
        env="DATABASE_URL"
    )
    
    # Redis (for caching)
    redis_url: Optional[str] = Field(default=None, env="REDIS_URL")
    
    # API Keys (stored securely)
    GOOGLE_API_KEY: Optional[str] = Field(default=None, env="GOOGLE_API_KEY")
    openai_api_key: Optional[str] = Field(default=None, env="OPENAI_API_KEY")
    anthropic_api_key: Optional[str] = Field(default=None, env="ANTHROPIC_API_KEY")
    
    # File paths
    base_dir: Path = _BASE_DIR # Set it directly

    # Initialize with a concrete Path object
    data_dir: Path = Field(default=_BASE_DIR / 'data')
    logs_dir: Path = Field(default=_BASE_DIR / 'logs')
    # For diary_storage_path, since it depends on data_dir which itself has a default
    # it's trickier to set a direct Field(default=...).
    # We'll use a model_validator for dependent defaults like this.
    diary_storage_path: Optional[Path] = None # Keep as Optional for now, validator will set it
    
    # Minion defaults
    default_model: str = Field(default="gemini-2.5-flash", env="DEFAULT_MODEL") # Changed default model
    default_temperature: float = Field(default=0.7, env="DEFAULT_TEMPERATURE")
    default_max_tokens: int = Field(default=4096, env="DEFAULT_MAX_TOKENS")
    
    # Communication settings
    max_messages_per_minute: int = Field(default=10, env="MAX_MESSAGES_PER_MINUTE")
    max_messages_per_hour: int = Field(default=60, env="MAX_MESSAGES_PER_HOUR")
    turn_cooldown_seconds: float = Field(default=2.0, env="TURN_COOLDOWN_SECONDS")
    
    # Safety settings
    max_minions: int = Field(default=20, env="MAX_MINIONS")
    max_channels: int = Field(default=50, env="MAX_CHANNELS")
    message_history_limit: int = Field(default=1000, env="MESSAGE_HISTORY_LIMIT")
    
    # Emotional engine settings
    max_mood_change_per_interaction: float = Field(default=0.3, env="MAX_MOOD_CHANGE")
    max_opinion_change_per_interaction: float = Field(default=25.0, env="MAX_OPINION_CHANGE")
    emotional_decay_rate: float = Field(default=0.95, env="EMOTIONAL_DECAY_RATE")
    
    # Memory settings
    working_memory_capacity: int = Field(default=7, env="WORKING_MEMORY_CAPACITY")
    episodic_memory_threshold: float = Field(default=0.5, env="EPISODIC_MEMORY_THRESHOLD")
    memory_consolidation_interval_hours: int = Field(default=24, env="MEMORY_CONSOLIDATION_INTERVAL")
    
    # Task settings
    default_task_timeout_seconds: int = Field(default=300, env="DEFAULT_TASK_TIMEOUT")
    max_concurrent_tasks_per_minion: int = Field(default=3, env="MAX_CONCURRENT_TASKS")
    
    # Feature flags
    enable_autonomous_messaging: bool = Field(default=True, env="ENABLE_AUTONOMOUS_MESSAGING")
    enable_inter_minion_chat: bool = Field(default=True, env="ENABLE_INTER_MINION_CHAT")
    enable_emotional_decay: bool = Field(default=True, env="ENABLE_EMOTIONAL_DECAY")
    enable_memory_consolidation: bool = Field(default=False, env="ENABLE_MEMORY_CONSOLIDATION")

    @model_validator(mode='after')
    def set_derived_paths(self) -> 'Settings': # Changed signature to use self
        # Access fields directly from the model instance (self)
        base_dir_val = self.base_dir
        data_dir_val = self.data_dir

        if self.diary_storage_path is None:
            if isinstance(data_dir_val, Path):
                self.diary_storage_path = data_dir_val / "diaries"
            elif isinstance(base_dir_val, Path):
                # This case implies data_dir_val might not have been a Path initially,
                # which shouldn't happen if Field(default=...) for data_dir is correct.
                # However, providing a fallback based on base_dir.
                self.diary_storage_path = base_dir_val / "data" / "diaries"
            else:
                # Failsafe if base_dir itself isn't a Path (should be caught by its own type validation)
                # This indicates a more fundamental issue with _BASE_DIR or base_dir assignment.
                # For robustness, create a path relative to this file, though it's not ideal.
                self.diary_storage_path = Path(__file__).resolve().parent.parent / "data" / "diaries_fallback_validator"

        # Ensure all path fields are Path objects after potential modifications or if loaded as strings from .env
        # data_dir and logs_dir should already be Path objects due to their Field(default=...)
        # This is an extra check or conversion if they were somehow overridden by non-Path values (e.g. from .env as str)
        if self.data_dir is not None and not isinstance(self.data_dir, Path):
            self.data_dir = Path(self.data_dir)
        if self.logs_dir is not None and not isinstance(self.logs_dir, Path):
            self.logs_dir = Path(self.logs_dir)
        if self.diary_storage_path is not None and not isinstance(self.diary_storage_path, Path):
            self.diary_storage_path = Path(self.diary_storage_path)

        # If any path is still None after the above (e.g., if .env set them to empty string, which Pydantic might convert to None for Optional types)
        # re-default them based on base_dir. This ensures they are always Path objects.
        if self.data_dir is None: # Should be covered by Field(default=...)
             self.data_dir = self.base_dir / 'data'
        if self.logs_dir is None: # Should be covered by Field(default=...)
             self.logs_dir = self.base_dir / 'logs'
        if self.diary_storage_path is None: # If all prior logic failed to set it
             self.diary_storage_path = self.data_dir / "diaries" # Relies on data_dir being a Path now

        return self # Return the modified model instance
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        # After model_validator, these should be Path objects.
        # Assertions to make double sure before mkdir.
        # These assertions are critical for debugging if the validator logic is somehow bypassed or flawed.
        if not isinstance(self.data_dir, Path):
            raise TypeError(f"Settings.data_dir was not initialized as a Path. Got: {type(self.data_dir)}")
        if not isinstance(self.logs_dir, Path):
            raise TypeError(f"Settings.logs_dir was not initialized as a Path. Got: {type(self.logs_dir)}")
        if not isinstance(self.diary_storage_path, Path):
            raise TypeError(f"Settings.diary_storage_path was not initialized as a Path. Got: {type(self.diary_storage_path)}")

        # Create directories
        self.data_dir.mkdir(exist_ok=True)
        self.logs_dir.mkdir(exist_ok=True)
        self.diary_storage_path.mkdir(exist_ok=True)
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


# Global settings instance
settings = Settings()
