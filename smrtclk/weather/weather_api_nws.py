import time
import warnings

import requests
from requests.adapters import HTTPAdapter
from urllib3.util import Retry

from .weather_api import WeatherAPI

BASE_API_URL = "https://api.weather.gov/"
POINTS_URL = "points/"
GRIDPOINTS_URL = "gridpoints/"
FORECAST_URL = "forecast/"


def get_json_requests_retry(url: str) -> dict | None:
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
    UserWarning
        If there is an error getting the JSON data.
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
                f"Error getting JSON data: {r.status_code}\n\nJSON data will not be available.",
                stacklevel=2,
            )
            return
        # Return the JSON data
        return r.json()
    except Exception as e:
        warnings.warn(
            f"Error getting JSON data: {e}\n\nJSON data will not be available.",
            stacklevel=2,
        )
        return


class WeatherAPINWS(WeatherAPI):
    """Weather API that connects to the National Weather Service (NWS)."""

    def __init__(self, latitude: float, longitude: float):
        """Initializes the WeatherAPINWS class.

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

    @property
    def latitude(self):
        return self._latitude

    @property
    def longitude(self):
        return self._longitude

    @latitude.setter
    def latitude(self, latitude):
        if not isinstance(latitude, (int, float)):
            raise TypeError("Latitude must be an int or float")
        if latitude < -90 or latitude > 90:
            raise ValueError("Latitude must be between -90 and 90")
        self._latitude = latitude
        self._location_cache = None

    @longitude.setter
    def longitude(self, longitude):
        if not isinstance(longitude, (int, float)):
            raise TypeError("Longitude must be an int or float")
        if longitude < -180 or longitude > 180:
            raise ValueError("Longitude must be between -180 and 180")
        self._longitude = longitude
        self._location_cache = None

    def _get_location(self) -> None:
        """Gets the location of the given latitude and longitude for use with the NWS API."""
        # If the location cache is not None, return
        if self._location_cache is not None:
            return
        # Get the URL for the location
        url = f"{BASE_API_URL}{POINTS_URL}{self.latitude},{self.longitude}"
        # Get the location data with retry
        location_data = get_json_requests_retry(url)
        # Cache the location data
        if location_data is not None:
            self._location_cache = f"{location_data['properties']['gridId']}/{location_data['properties']['gridX']},{location_data['properties']['gridY']}"

    def _get_forecast(self) -> None:
        """Gets the forecast data for the given latitude and longitude."""
        # If the location cache is None, get the location data
        if self._location_cache is None:
            self._get_location()
        # Get the URL for the forecast
        url = f"{BASE_API_URL}{GRIDPOINTS_URL}{self._location_cache}/{FORECAST_URL}"
        # Get the forecast data with retry
        forecast_data = get_json_requests_retry(url)
        # Cache the forecast data
        if forecast_data is not None:
            self._forecast_cache = forecast_data
            self._forecast_cache_date = time.strftime("%Y-%m-%d-%H-%M-%S")

    def _parse_forecast(self) -> dict:
        # Find the forecast periods for today and tonight
        if self._forecast_cache is None:
            return {}

        today, tonight = None, None
        for period in self._forecast_cache["properties"]["periods"]:
            if period["name"] == "Today":
                today = period  # noqa: F841
            elif period["name"] == "Tonight":
                tonight = period  # noqa: F841

        # Return weather data (placeholder implementation)
        return {}

    def _get_sunrise_sunset(self) -> dict | None:
        pass

    def get_current_weather(self) -> dict:
        """Gets the current weather for the given location. The return value is a dictionary with the weather data.

        It is expected that the dictionary will have the following keys:
        - temperature: The current temperature in degrees Fahrenheit.
        - temperature_min: The minimum temperature for the day in degrees Fahrenheit.
        - temperature_max: The maximum temperature for the day in degrees Fahrenheit.
        - precipitation: The current chance of precipitation percentage.
        - precipitation_min: The minimum chance of precipitation percentage for the day.
        - precipitation_max: The maximum chance of precipitation percentage for the day.
        - sunrise: The time of sunrise in the format HH:MM.
        - sunset: The time of sunset in the format HH:MM.

        Returns
        -------
        dict
            The current weather data.
        """
        self._get_forecast()
        return self._parse_forecast()
