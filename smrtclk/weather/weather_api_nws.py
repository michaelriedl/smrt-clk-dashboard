import logging
import math
from datetime import datetime, timezone, timedelta

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

        Raises
        ------
        ValueError
            If no forecast periods are present in the response.
        """
        periods = raw_data.get("properties", {}).get("periods", [])
        if not periods:
            raise ValueError("No forecast periods found in NWS response")

        first = periods[0]
        first_day = next((p for p in periods if p.get("isDaytime")), None)
        first_night = next((p for p in periods if not p.get("isDaytime")), None)

        def to_fahrenheit(period: dict) -> float:
            temp = float(period["temperature"])
            if period.get("temperatureUnit") == "C":
                temp = temp * 9 / 5 + 32
            return temp

        def get_precip(period: dict) -> int:
            val = period.get("probabilityOfPrecipitation", {}).get("value")
            return int(val) if val is not None else 0

        current_temp = to_fahrenheit(first)
        temp_max = to_fahrenheit(first_day) if first_day else current_temp
        temp_min = to_fahrenheit(first_night) if first_night else current_temp

        # Use up to the first 4 periods (~2 days) for precip range
        precip_sample = [get_precip(p) for p in periods[:4]]
        current_precip = get_precip(first)
        precip_min = min(precip_sample)
        precip_max = max(precip_sample)

        # Derive local UTC offset from the first period's startTime
        utc_offset_hours = self._parse_utc_offset(first.get("startTime", ""))
        sunrise, sunset = self._calculate_sunrise_sunset(utc_offset_hours)

        weather_data: WeatherData = {
            "temperature": current_temp,
            "temperature_min": temp_min,
            "temperature_max": temp_max,
            "precipitation": current_precip,
            "precipitation_min": precip_min,
            "precipitation_max": precip_max,
            "sunrise": sunrise,
            "sunset": sunset,
        }

        logger.info(
            f"NWS weather parsed: {current_temp:.1f}°F "
            f"(min {temp_min:.1f}, max {temp_max:.1f}), "
            f"{current_precip}% precip, "
            f"sunrise {sunrise}, sunset {sunset}"
        )
        return weather_data

    def _parse_utc_offset(self, iso_timestamp: str) -> float:
        """Extract UTC offset in hours from an ISO 8601 timestamp string.

        Parameters
        ----------
        iso_timestamp : str
            Timestamp like "2026-04-20T18:00:00-04:00".

        Returns
        -------
        float
            UTC offset in hours (e.g. -4.0). Returns local system offset on parse failure.
        """
        try:
            # Last 6 chars are ±HH:MM
            sign = 1 if iso_timestamp[-6] == "+" else -1
            hh = int(iso_timestamp[-5:-3])
            mm = int(iso_timestamp[-2:])
            return sign * (hh + mm / 60)
        except (IndexError, ValueError):
            logger.warning("Could not parse UTC offset from timestamp; using system local time")
            return datetime.now().astimezone().utcoffset().total_seconds() / 3600

    def _calculate_sunrise_sunset(self, utc_offset_hours: float) -> tuple[str, str]:
        """Calculate sunrise and sunset times using a simplified astronomical formula.

        Parameters
        ----------
        utc_offset_hours : float
            Local UTC offset in hours (e.g. -4.0 for EDT).

        Returns
        -------
        tuple[str, str]
            Sunrise and sunset times as "HH:MM" strings in local time.
        """
        day_of_year = datetime.now().timetuple().tm_yday
        lat_rad = math.radians(self.latitude)

        # Solar declination (degrees), accurate to ~1°
        decl = math.radians(
            -23.45 * math.cos(math.radians(360 / 365 * (day_of_year + 10)))
        )

        # Hour angle at sunrise/sunset (cos = 0 at equator equinox)
        cos_ha = -math.tan(lat_rad) * math.tan(decl)
        cos_ha = max(-1.0, min(1.0, cos_ha))
        hour_angle_deg = math.degrees(math.acos(cos_ha))

        # Approximate solar noon in UTC (ignores equation of time, ~±16 min error)
        solar_noon_utc = 12.0 - self.longitude / 15.0
        sunrise_utc = solar_noon_utc - hour_angle_deg / 15.0
        sunset_utc = solar_noon_utc + hour_angle_deg / 15.0

        sunrise_local = (sunrise_utc + utc_offset_hours) % 24
        sunset_local = (sunset_utc + utc_offset_hours) % 24

        def to_hhmm(decimal_hours: float) -> str:
            h = int(decimal_hours)
            m = round((decimal_hours - h) * 60)
            if m == 60:
                h += 1
                m = 0
            return f"{h:02d}:{m:02d}"

        return to_hhmm(sunrise_local), to_hhmm(sunset_local)
