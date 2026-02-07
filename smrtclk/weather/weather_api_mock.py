"""Mock implementation of WeatherAPI for testing and development."""

import logging
import random

from .weather_api import WeatherAPI, WeatherData

logger = logging.getLogger(__name__)


class WeatherAPIMock(WeatherAPI):
    """Mock Weather API for testing and development.

    Provides realistic but static/randomized weather data without
    making any network calls. Useful for developing the UI and testing
    the application without depending on external APIs.
    """

    def __init__(
        self,
        latitude: float = 39.7392,
        longitude: float = -104.9903,
        cache_duration: int = 900,
        scenario: str = "sunny",
    ):
        """Initialize the mock weather API.

        Parameters
        ----------
        latitude : float, optional
            The latitude of the location (default: Denver, CO).
        longitude : float, optional
            The longitude of the location (default: Denver, CO).
        cache_duration : int, optional
            Cache duration in seconds (default: 900 = 15 minutes).
        scenario : str, optional
            Weather scenario to simulate: "sunny", "rainy", "cloudy",
            "stormy", "extreme_heat", "extreme_cold", "random"
            (default: "sunny").
        """
        self._scenario = scenario
        super().__init__(latitude, longitude, cache_duration)
        logger.info(f"Mock weather API initialized with scenario: {scenario}")

    @property
    def scenario(self) -> str:
        """Get the current weather scenario."""
        return self._scenario

    @scenario.setter
    def scenario(self, scenario: str) -> None:
        """Set the weather scenario and invalidate cache.

        Parameters
        ----------
        scenario : str
            The weather scenario: "sunny", "rainy", "cloudy", "stormy",
            "extreme_heat", "extreme_cold", "random".
        """
        valid_scenarios = [
            "sunny",
            "rainy",
            "cloudy",
            "stormy",
            "extreme_heat",
            "extreme_cold",
            "random",
        ]
        if scenario not in valid_scenarios:
            raise ValueError(
                f"Invalid scenario '{scenario}'. "
                f"Must be one of: {', '.join(valid_scenarios)}"
            )
        self._scenario = scenario
        self._invalidate_cache()
        logger.info(f"Weather scenario changed to: {scenario}")

    def _fetch_weather_data(self) -> dict:
        """Fetch mock weather data.

        Returns
        -------
        dict
            Mock weather data based on the current scenario.
        """
        logger.debug(f"Generating mock weather data for scenario: {self._scenario}")
        # Simulate a brief "network delay" by returning immediately
        # (no actual delay - this is instant)
        return {"scenario": self._scenario}

    def _parse_weather_data(self, raw_data: dict) -> WeatherData:
        """Parse mock weather data into standardized format.

        Parameters
        ----------
        raw_data : dict
            Raw data containing scenario information.

        Returns
        -------
        WeatherData
            Realistic mock weather data based on the scenario.
        """
        scenario = raw_data.get("scenario", "sunny")

        # Generate realistic data based on scenario
        if scenario == "random":
            scenario = random.choice(
                ["sunny", "rainy", "cloudy", "stormy", "extreme_heat", "extreme_cold"]
            )
            logger.debug(f"Random scenario selected: {scenario}")

        weather_data = self._generate_scenario_data(scenario)

        # Add sunrise and sunset times (varies slightly by location)
        # Using approximate times for mid-latitudes
        sunrise_time = self._calculate_sunrise()
        sunset_time = self._calculate_sunset()
        weather_data["sunrise"] = sunrise_time
        weather_data["sunset"] = sunset_time

        logger.debug(f"Generated weather data: {weather_data}")
        return weather_data

    def _generate_scenario_data(self, scenario: str) -> WeatherData:
        """Generate weather data for a specific scenario.

        Parameters
        ----------
        scenario : str
            The weather scenario.

        Returns
        -------
        WeatherData
            Weather data for the scenario (without sunrise/sunset).
        """
        if scenario == "sunny":
            return {
                "temperature": 72.0,
                "temperature_min": 65.0,
                "temperature_max": 78.0,
                "precipitation": 5,
                "precipitation_min": 0,
                "precipitation_max": 10,
            }
        elif scenario == "rainy":
            return {
                "temperature": 58.0,
                "temperature_min": 55.0,
                "temperature_max": 62.0,
                "precipitation": 75,
                "precipitation_min": 60,
                "precipitation_max": 85,
            }
        elif scenario == "cloudy":
            return {
                "temperature": 64.0,
                "temperature_min": 60.0,
                "temperature_max": 68.0,
                "precipitation": 30,
                "precipitation_min": 20,
                "precipitation_max": 40,
            }
        elif scenario == "stormy":
            return {
                "temperature": 55.0,
                "temperature_min": 52.0,
                "temperature_max": 58.0,
                "precipitation": 95,
                "precipitation_min": 90,
                "precipitation_max": 100,
            }
        elif scenario == "extreme_heat":
            return {
                "temperature": 105.0,
                "temperature_min": 95.0,
                "temperature_max": 110.0,
                "precipitation": 0,
                "precipitation_min": 0,
                "precipitation_max": 5,
            }
        elif scenario == "extreme_cold":
            return {
                "temperature": -5.0,
                "temperature_min": -15.0,
                "temperature_max": 5.0,
                "precipitation": 45,
                "precipitation_min": 30,
                "precipitation_max": 60,
            }
        else:
            # Default to sunny
            logger.warning(f"Unknown scenario '{scenario}', defaulting to sunny")
            return self._generate_scenario_data("sunny")

    def _calculate_sunrise(self) -> str:
        """Calculate approximate sunrise time based on latitude.

        Returns
        -------
        str
            Sunrise time in HH:MM format.
        """
        # Simplified calculation - varies by latitude and time of year
        # Positive latitude (northern hemisphere): earlier sunrise in summer
        # This is a very rough approximation for demonstration
        base_hour = 6
        base_minute = 30

        # Adjust slightly based on latitude (very simplified)
        latitude_offset = int(abs(self.latitude) / 10)  # 0-9 minutes
        if self.latitude > 0:
            # Northern hemisphere
            base_minute += latitude_offset
        else:
            # Southern hemisphere
            base_minute -= latitude_offset

        # Normalize minutes
        if base_minute >= 60:
            base_hour += 1
            base_minute -= 60
        elif base_minute < 0:
            base_hour -= 1
            base_minute += 60

        return f"{base_hour:02d}:{base_minute:02d}"

    def _calculate_sunset(self) -> str:
        """Calculate approximate sunset time based on latitude.

        Returns
        -------
        str
            Sunset time in HH:MM format.
        """
        # Simplified calculation - varies by latitude and time of year
        base_hour = 18
        base_minute = 45

        # Adjust slightly based on latitude (very simplified)
        latitude_offset = int(abs(self.latitude) / 10)  # 0-9 minutes
        if self.latitude > 0:
            # Northern hemisphere
            base_minute += latitude_offset
        else:
            # Southern hemisphere
            base_minute -= latitude_offset

        # Normalize minutes
        if base_minute >= 60:
            base_hour += 1
            base_minute -= 60
        elif base_minute < 0:
            base_hour -= 1
            base_minute += 60

        return f"{base_hour:02d}:{base_minute:02d}"

    def set_temperature(self, current: float, min_temp: float, max_temp: float) -> None:
        """Set custom temperature values and invalidate cache.

        Useful for testing specific temperature scenarios.

        Parameters
        ----------
        current : float
            Current temperature in Fahrenheit.
        min_temp : float
            Minimum temperature for the day in Fahrenheit.
        max_temp : float
            Maximum temperature for the day in Fahrenheit.
        """
        self._custom_temp = (current, min_temp, max_temp)
        self._invalidate_cache()
        logger.info(
            f"Custom temperature set: {current}°F (min: {min_temp}, max: {max_temp})"
        )

    def set_precipitation(self, current: int, min_precip: int, max_precip: int) -> None:
        """Set custom precipitation values and invalidate cache.

        Useful for testing specific precipitation scenarios.

        Parameters
        ----------
        current : int
            Current precipitation probability (0-100).
        min_precip : int
            Minimum precipitation probability for the day (0-100).
        max_precip : int
            Maximum precipitation probability for the day (0-100).
        """
        self._custom_precip = (current, min_precip, max_precip)
        self._invalidate_cache()
        logger.info(
            f"Custom precipitation set: {current}% (min: {min_precip}, max: {max_precip})"
        )
