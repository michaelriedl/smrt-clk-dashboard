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
        pass
