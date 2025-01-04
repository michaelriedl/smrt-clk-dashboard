import time

BASE_API_URL = "https://api.weather.gov/"
POINTS_URL = "points/"
GRIDPOINTS_URL = "gridpoints/"
FORECAST_URL = "forecast/"


class WeatherAPI:
    """Class to handle the weather API"""

    def __init__(self):
        self.current_date = time.strftime("%Y-%m-%d")
        self._location_cache = None
        self._forecast_cache = None
