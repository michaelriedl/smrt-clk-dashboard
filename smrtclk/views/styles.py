"""Centralized styling for Smart Clock Dashboard."""

from config.constants import (
    PRIMARY_COLOR,
    BASE_FONT_FAMILY,
    DATE_FONT_SIZE_BASE,
    TIME_FONT_SIZE_BASE,
    TEMP_FONT_SIZE_BASE,
    TEMP_CUR_FONT_SIZE_BASE
)


class Styles:
    """
    Centralized styling constants and methods.
    
    Provides consistent styling across all widgets with support
    for scaling based on display resolution.
    """
    
    @staticmethod
    def get_background_style(image_path: str) -> str:
        """
        Get stylesheet for background frame.
        
        Args:
            image_path: Path to background image
            
        Returns:
            QSS stylesheet string
        """
        return (
            "#background { "
            f"background-color: black; "
            f"border-image: url({image_path}) 0 0 0 0 stretch stretch;"
            "}"
        )
    
    @staticmethod
    def get_transparent_style(object_name: str) -> str:
        """
        Get stylesheet for transparent widget.
        
        Args:
            object_name: Object name for CSS selector
            
        Returns:
            QSS stylesheet string
        """
        return f"#{object_name} {{ background-color: transparent; }}"
    
    @staticmethod
    def get_text_style(
        object_name: str,
        font_size: int,
        color: str = PRIMARY_COLOR,
        font_family: str = BASE_FONT_FAMILY
    ) -> str:
        """
        Get stylesheet for text labels.
        
        Args:
            object_name: Object name for CSS selector
            font_size: Font size in pixels
            color: Text color
            font_family: Font family name
            
        Returns:
            QSS stylesheet string
        """
        return (
            f"#{object_name} {{ "
            f"font-family: {font_family}; "
            f"color: {color}; "
            f"background-color: transparent; "
            f"font-size: {font_size}px; "
            f"}}"
        )
    
    @staticmethod
    def get_clockface_style(image_path: str) -> str:
        """
        Get stylesheet for clock face.
        
        Args:
            image_path: Path to clock face image
            
        Returns:
            QSS stylesheet string
        """
        return (
            "#clockface { "
            f"background-color: transparent; "
            f"border-image: url({image_path}) 0 0 0 0 stretch stretch;"
            "}"
        )
