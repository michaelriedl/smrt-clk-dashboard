import time
import warnings

import requests
from requests.adapters import HTTPAdapter
from urllib3.util import Retry

BASE_API_URL = "https://api.weather.gov/"
POINTS_URL = "points/"
GRIDPOINTS_URL = "gridpoints/"
FORECAST_URL = "forecast/"


class WeatherAPI:
    """Class to handle the weather API."""

    def __init__(self, latitude: float, longitude: float):
        """Initializes the WeatherAPI class.

        Parameters
        ----------
        latitude : float
            The latitude of the location to get the weather for.
        longitude : float
            The longitude of the location to get the weather for.
        """
        # Store the latitude and longitude
        self.latitude = latitude
        self.longitude = longitude
        # Create the needed variables for the class
        self.current_date = time.strftime("%Y-%m-%d")
        self._location_cache = None
        self._forecast_cache = None
        self._forecast_cache_date = None

    def _get_location(self):
        """Gets the location of the given latitude and longitude for use with the API."""
        # Get the URL for the location
        url = f"{BASE_API_URL}{POINTS_URL}{self.latitude},{self.longitude}"
        # Get the location data with retry
        try:
            # Setup the retry strategy
            retry = Retry(
                total=5,
                backoff_factor=2,
                status_forcelist=[429, 500, 502, 503, 504],
            )
            # Create the HTTP adapter
            adapter = HTTPAdapter(max_retries=retry)
            # Create the session
            session = requests.Session()
            session.mount("https://", adapter)
            # Get the location data
            r = session.get(url)
            if r.status_code != 200:
                warnings.warn(
                    f"Error getting location data: {r.status_code}\n\nLocation data will not be available."
                )
                return
            # Extract the location data from the response JSON
            location_data = r.json()
            # Cache the location data
            self._location_cache = f"{location_data['properties']['gridX']},{location_data['properties']['gridY']}"

        except Exception as e:
            warnings.warn(
                f"Error getting location data: {e}\n\nLocation data will not be available."
            )
