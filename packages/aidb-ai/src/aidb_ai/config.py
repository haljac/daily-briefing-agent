"""Configuration management with XDG Base Directory support."""

import tomllib
from pathlib import Path

import tomli_w
from pydantic import BaseModel, Field


class UserConfig(BaseModel):
    """User configuration model."""

    zip_code: str | None = Field(None, description="User's zip code for weather information")


class ConfigManager:
    """Manages application configuration using XDG Base Directory specification."""

    def __init__(self, app_name: str = "aidb"):
        self.app_name = app_name
        # Always use ~/.config/aidb/ regardless of OS
        self._config_dir = Path.home() / ".config" / app_name
        self._config_file = self._config_dir / "config.toml"
        self._config: UserConfig | None = None

    @property
    def config_dir(self) -> Path:
        """Get the configuration directory path."""
        return self._config_dir

    @property
    def config_file(self) -> Path:
        """Get the configuration file path."""
        return self._config_file

    def _ensure_config_dir(self) -> None:
        """Ensure the configuration directory exists."""
        self._config_dir.mkdir(parents=True, exist_ok=True)

    def load_config(self) -> UserConfig:
        """Load configuration from file, creating defaults if needed."""
        if self._config is not None:
            return self._config

        if self._config_file.exists():
            try:
                with self._config_file.open("rb") as f:
                    config_data = tomllib.load(f)
                self._config = UserConfig(**config_data)
            except (tomllib.TOMLDecodeError, TypeError, ValueError):
                # If config file is corrupted, start with defaults
                self._config = UserConfig()
        else:
            # Create default configuration
            self._config = UserConfig()

        return self._config

    def save_config(self, config: UserConfig | None = None) -> None:
        """Save configuration to file."""
        if config is not None:
            self._config = config

        if self._config is None:
            return

        self._ensure_config_dir()

        # Convert to dict and write TOML
        config_data = self._config.model_dump(exclude_none=True)

        with self._config_file.open("wb") as f:
            tomli_w.dump(config_data, f)

    def update_zip_code(self, zip_code: str) -> None:
        """Update the zip code in configuration."""
        config = self.load_config()
        config.zip_code = zip_code
        self._config = config
        self.save_config()

    def get_zip_code(self) -> str | None:
        """Get the configured zip code."""
        config = self.load_config()
        return config.zip_code

    def needs_zip_code(self) -> bool:
        """Check if zip code is needed (not configured)."""
        return self.get_zip_code() is None
