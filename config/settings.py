"""Configuration management for Smart Clock Dashboard."""

import os
from typing import Optional
from pathlib import Path


class Config:
    """
    Configuration class for the Smart Clock Dashboard application.
    
    Manages application settings including API keys, location data,
    display settings, and file paths.
    """
    
    def __init__(
        self,
        latitude: str = "40.0931191",
        longitude: str = "-83.017962",
        api_key: Optional[str] = None,
        width: int = 480,
        height: int = 272,
        images_path: Optional[Path] = None
    ):
        """
        Initialize configuration.
        
        Args:
            latitude: Geographic latitude for weather data
            longitude: Geographic longitude for weather data
            api_key: OpenWeatherMap API key (optional)
            width: Display width in pixels
            height: Display height in pixels
            images_path: Path to images directory
        """
        self.latitude = latitude
        self.longitude = longitude
        self.api_key = api_key
        self.width = width
        self.height = height
        self.images_path = images_path or Path(__file__).parent.parent / "images"
        
        # Calculate scale factors
        self.xscale = float(width) / 1440.0
        self.yscale = float(height) / 900.0
    
    @classmethod
    def from_env(cls) -> 'Config':
        """
        Create configuration from environment variables.
        
        Returns:
            Config instance populated from environment variables
        """
        # TODO: Implement loading from environment variables
        # Will use python-dotenv to load .env file
        return cls()
    
    @classmethod
    def from_file(cls, config_path: Path) -> 'Config':
        """
        Create configuration from a config file.
        
        Args:
            config_path: Path to configuration file
            
        Returns:
            Config instance populated from file
        """
        # TODO: Implement loading from config file (JSON or TOML)
        return cls()
