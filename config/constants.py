"""Constants for Smart Clock Dashboard application."""

# Timer intervals (milliseconds)
CLOCK_UPDATE_INTERVAL = 1000  # 1 second
WEATHER_UPDATE_INTERVAL = 5 * 60 * 1000  # 5 minutes

# Color constants
PRIMARY_COLOR = "#bef"
BACKGROUND_COLOR = "black"

# Font settings
BASE_FONT_FAMILY = "sans-serif"
DATE_FONT_SIZE_BASE = 70
TIME_FONT_SIZE_BASE = 40
TEMP_FONT_SIZE_BASE = 50
TEMP_CUR_FONT_SIZE_BASE = 45

# Widget dimensions (relative to base 1440x900 resolution)
CLOCK_FACE_SIZE_RATIO = 0.8
CLOCK_CENTER_X_RATIO = 0.5
CLOCK_CENTER_Y_RATIO = 0.45

# Image paths (relative to images directory)
BACKGROUND_IMAGE = "clockbackground_small.png"
CLOCK_FACE_IMAGE = "clockface3.png"
HOUR_HAND_IMAGE = "hourhand.png"
MINUTE_HAND_IMAGE = "minhand.png"
SECOND_HAND_IMAGE = "sechand.png"
SUNRISE_ICON = "sun-rise.png"
SLIDER_BAR_IMAGE = "slider-bar.png"
SLIDER_IMAGE = "slider.png"

# Weather API settings
DEFAULT_LATITUDE = "40.0931191"
DEFAULT_LONGITUDE = "-83.017962"
