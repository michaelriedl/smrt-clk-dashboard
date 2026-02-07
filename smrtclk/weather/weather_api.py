import logging
import time
from abc import ABC, abstractmethod
from typing import TypedDict

logger = logging.getLogger(__name__)


class WeatherData(TypedDict, total=False):
    """Type definition for weather data returned by WeatherAPI.

    Attributes
    ----------
    status : str
        Status of the weather data fetch: "ok", "error", or "cached".
    error_message : str
        Error message if status is "error".
    temperature : float
        Current temperature in degrees Fahrenheit.
    temperature_min : float
        Minimum temperature for the day in degrees Fahrenheit.
    temperature_max : float
        Maximum temperature for the day in degrees Fahrenheit.
    precipitation : int
        Current chance of precipitation percentage (0-100).
    precipitation_min : int
        Minimum chance of precipitation percentage for the day (0-100).
    precipitation_max : int
        Maximum chance of precipitation percentage for the day (0-100).
    sunrise : str
        Time of sunrise in the format HH:MM.
    sunset : str
        Time of sunset in the format HH:MM.
    """

    status: str
    error_message: str
    temperature: float
    temperature_min: float
    temperature_max: float
    precipitation: int
    precipitation_min: int
    precipitation_max: int
    sunrise: str
    sunset: str


class WeatherAPI(ABC):
    """Abstract base class for weather API implementations.

    Provides common functionality for latitude/longitude validation,
    caching, and the template method pattern for fetching weather data.
    """

    def __init__(self, latitude: float, longitude: float, cache_duration: int = 900):
        """Initializes the WeatherAPI class.

        Parameters
        ----------
        latitude : float
            The latitude of the location to get the weather for.
        longitude : float
            The longitude of the location to get the weather for.
        cache_duration : int, optional
            Cache duration in seconds (default: 900 = 15 minutes).
        """
        # Store cache duration
        self._cache_duration = cache_duration
        # Initialize cache
        self._weather_cache: WeatherData | None = None
        self._cache_timestamp: float | None = None
        # Set latitude and longitude (triggers validation and cache invalidation)
        self.latitude = latitude
        self.longitude = longitude

    @property
    def latitude(self) -> float:
        """Get the latitude."""
        return self._latitude

    @latitude.setter
    def latitude(self, latitude: float) -> None:
        """Set the latitude with validation.

        Parameters
        ----------
        latitude : float
            The latitude value (-90 to 90).

        Raises
        ------
        TypeError
            If latitude is not a number.
        ValueError
            If latitude is outside the valid range.
        """
        if not isinstance(latitude, (int, float)):
            raise TypeError("Latitude must be an int or float")
        if latitude < -90 or latitude > 90:
            raise ValueError("Latitude must be between -90 and 90")
        self._latitude = latitude
        # Invalidate cache when location changes
        self._invalidate_cache()

    @property
    def longitude(self) -> float:
        """Get the longitude."""
        return self._longitude

    @longitude.setter
    def longitude(self, longitude: float) -> None:
        """Set the longitude with validation.

        Parameters
        ----------
        longitude : float
            The longitude value (-180 to 180).

        Raises
        ------
        TypeError
            If longitude is not a number.
        ValueError
            If longitude is outside the valid range.
        """
        if not isinstance(longitude, (int, float)):
            raise TypeError("Longitude must be an int or float")
        if longitude < -180 or longitude > 180:
            raise ValueError("Longitude must be between -180 and 180")
        self._longitude = longitude
        # Invalidate cache when location changes
        self._invalidate_cache()

    def _invalidate_cache(self) -> None:
        """Invalidate the weather data cache."""
        self._weather_cache = None
        self._cache_timestamp = None
        logger.debug("Weather cache invalidated")

    def _is_cache_valid(self) -> bool:
        """Check if the cached weather data is still valid.

        Returns
        -------
        bool
            True if cache exists and hasn't expired, False otherwise.
        """
        if self._weather_cache is None or self._cache_timestamp is None:
            return False

        age = time.time() - self._cache_timestamp
        is_valid = age < self._cache_duration

        if not is_valid:
            logger.debug(
                f"Cache expired (age: {age:.1f}s, max: {self._cache_duration}s)"
            )

        return is_valid

    def refresh(self) -> None:
        """Force refresh of weather data by invalidating cache."""
        logger.info("Forcing weather data refresh")
        self._invalidate_cache()
        self.get_current_weather()  # Fetch new data immediately after refresh

    def get_current_weather(self) -> WeatherData:
        """Gets the current weather for the given location.

        This method uses caching to avoid excessive API calls. If cached data
        is available and fresh, it returns the cached data. Otherwise, it
        fetches new data from the API.

        Returns
        -------
        WeatherData
            Dictionary with weather data and status information.
        """
        # Return cached data if valid
        if self._is_cache_valid():
            logger.debug("Returning cached weather data")
            cached_data = self._weather_cache.copy() if self._weather_cache else {}
            cached_data["status"] = "cached"
            return cached_data

        # Fetch fresh data
        try:
            logger.info(
                f"Fetching weather data for ({self.latitude}, {self.longitude})"
            )
            raw_data = self._fetch_weather_data()
            weather_data = self._parse_weather_data(raw_data)

            # Add success status if not already set
            if "status" not in weather_data:
                weather_data["status"] = "ok"

            # Cache the result
            self._weather_cache = weather_data
            self._cache_timestamp = time.time()

            logger.info("Weather data fetched successfully")
            return weather_data

        except Exception as e:
            logger.error(f"Error fetching weather data: {e}", exc_info=True)
            # Return error status
            error_data: WeatherData = {
                "status": "error",
                "error_message": str(e),
            }
            return error_data

    @abstractmethod
    def _fetch_weather_data(self) -> dict:
        """Fetch raw weather data from the API.

        Subclasses must implement this method to retrieve data from
        their specific weather API source.

        Returns
        -------
        dict
            Raw weather data from the API.

        Raises
        ------
        Exception
            If there's an error fetching the data.
        """
        pass

    @abstractmethod
    def _parse_weather_data(self, raw_data: dict) -> WeatherData:
        """Parse raw weather data into standardized format.

        Subclasses must implement this method to convert their API-specific
        data format into the WeatherData format.

        Parameters
        ----------
        raw_data : dict
            Raw weather data from _fetch_weather_data().

        Returns
        -------
        WeatherData
            Parsed and standardized weather data.
        """
        pass
