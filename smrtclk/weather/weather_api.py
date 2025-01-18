from abc import ABC, abstractmethod


class WeatherAPI(ABC):
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

    @abstractmethod
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
        pass
