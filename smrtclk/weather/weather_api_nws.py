import logging

import requests
from requests.adapters import HTTPAdapter
from urllib3.util import Retry

from .weather_api import WeatherAPI, WeatherData

logger = logging.getLogger(__name__)

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

    Raises
    ------
    Exception
        If there is an error getting the JSON data or non-200 status code.
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
            logger.error(f"Error getting JSON data: HTTP {r.status_code}")
            raise Exception(f"HTTP {r.status_code}: Failed to retrieve data from {url}")
        # Return the JSON data
        return r.json()
    except requests.exceptions.RequestException as e:
        logger.error(f"Request error getting JSON data: {e}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error getting JSON data: {e}")
        raise


class WeatherAPINWS(WeatherAPI):
    """Weather API that connects to the National Weather Service (NWS)."""

    def __init__(self, latitude: float, longitude: float, cache_duration: int = 900):
        """Initializes the WeatherAPINWS class.

        Parameters
        ----------
        latitude : float
            The latitude of the location to get the weather for.
        longitude : float
            The longitude of the location to get the weather for.
        cache_duration : int, optional
            Cache duration in seconds (default: 900 = 15 minutes).
        """
        # Call parent constructor
        super().__init__(latitude, longitude, cache_duration)
        # NWS-specific cache for location data
        self._location_cache: str | None = None

    def _get_location(self) -> str:
        """Gets the location of the given latitude and longitude for use with the NWS API.

        Returns
        -------
        str
            The grid location string (e.g., "TOP/31,80").

        Raises
        ------
        Exception
            If unable to retrieve location data.
        """
        # If the location cache is not None, return it
        if self._location_cache is not None:
            return self._location_cache

        # Get the URL for the location
        url = f"{BASE_API_URL}{POINTS_URL}{self.latitude},{self.longitude}"
        logger.debug(f"Fetching NWS location data from: {url}")

        # Get the location data with retry
        location_data = get_json_requests_retry(url)

        # Cache and return the location data
        self._location_cache = (
            f"{location_data['properties']['gridId']}/"
            f"{location_data['properties']['gridX']},"
            f"{location_data['properties']['gridY']}"
        )
        logger.info(f"NWS location resolved to: {self._location_cache}")
        return self._location_cache

    def _invalidate_cache(self) -> None:
        """Override to also invalidate NWS-specific location cache."""
        super()._invalidate_cache()
        self._location_cache = None

    def _fetch_weather_data(self) -> dict:
        """Fetch raw weather data from NWS API.

        Returns
        -------
        dict
            Raw forecast data from NWS API.

        Raises
        ------
        Exception
            If unable to retrieve forecast data.
        """
        # Get the location grid coordinates
        location = self._get_location()

        # Get the URL for the forecast
        url = f"{BASE_API_URL}{GRIDPOINTS_URL}{location}/{FORECAST_URL}"
        logger.debug(f"Fetching NWS forecast from: {url}")

        # Get and return the forecast data with retry
        forecast_data = get_json_requests_retry(url)
        logger.info("NWS forecast data retrieved successfully")

        return forecast_data

    def _parse_weather_data(self, raw_data: dict) -> WeatherData:
        """Parse NWS forecast data into standardized format.

        Parameters
        ----------
        raw_data : dict
            Raw forecast data from NWS API.

        Returns
        -------
        WeatherData
            Parsed weather data.

        Note
        ----
        This is a placeholder implementation that needs to be completed.
        Currently returns empty/default values.
        """
        # TODO: Complete implementation
        # Find the forecast periods for today and tonight
        periods = raw_data.get("properties", {}).get("periods", [])

        today, tonight = None, None
        for period in periods:
            if period["name"] == "Today":
                today = period
            elif period["name"] == "Tonight":
                tonight = period

        # Placeholder: Return minimal data structure
        # This needs proper implementation to extract temperature, precipitation, etc.
        weather_data: WeatherData = {
            "temperature": today.get("temperature", 70.0) if today else 70.0,
            "temperature_min": tonight.get("temperature", 50.0) if tonight else 50.0,
            "temperature_max": today.get("temperature", 75.0) if today else 75.0,
            "precipitation": 0,
            "precipitation_min": 0,
            "precipitation_max": 0,
            "sunrise": "06:30",  # TODO: Implement sunrise/sunset calculation
            "sunset": "18:30",
        }

        logger.warning(
            "NWS weather data parsing is incomplete - using placeholder values"
        )
        return weather_data
