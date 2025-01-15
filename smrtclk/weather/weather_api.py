import time
import warnings

import requests
from requests.adapters import HTTPAdapter
from urllib3.util import Retry

BASE_API_URL = "https://api.weather.gov/"
POINTS_URL = "points/"
GRIDPOINTS_URL = "gridpoints/"
FORECAST_URL = "forecast/"


def get_json_requests_retry(url: str) -> dict:
    """Get the JSON data from the given URL with retry.

    Parameters
    ----------
    url : str
        The URL to get the JSON data from.

    Returns
    -------
    dict
        The JSON data from the URL.
    """
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
        # Get the JSON data
        r = session.get(url)
        if r.status_code != 200:
            warnings.warn(
                f"Error getting JSON data: {r.status_code}\n\nJSON data will not be available."
            )
            return
        # Return the JSON data
        return r.json()
    except Exception as e:
        warnings.warn(
            f"Error getting JSON data: {e}\n\nJSON data will not be available."
        )
        return


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
        location_data = get_json_requests_retry(url)
        # Cache the location data
        if location_data is not None:
            self._location_cache = f"{location_data['properties']['gridId']}/{location_data['properties']['gridX']},{location_data['properties']['gridY']}"

    def _get_forecast(self):
        """Gets the forecast data for the given latitude and longitude."""
        # If the location cache is None, get the location data
        if self._location_cache is None:
            self._get_location()
        # Get the URL for the forecast
        url = f"{BASE_API_URL}{GRIDPOINTS_URL}{self._location_cache}/{FORECAST_URL}"
        # Get the forecast data with retry
        forecast_data = get_json_requests_retry(url)
        # Cache the forecast data
        self._forecast_cache = forecast_data
        self._forecast_cache_date = time.strftime("%Y-%m-%d-%H-%M-%S")

    def _get_sunrise_sunset(self):
        pass

    def get_current_weather(self):
        pass
