import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

import time

import dotenv
import pytest

from smrtclk.weather.weather_api import WeatherAPI

TEST_DIR = os.path.dirname(os.path.abspath(__file__))


@pytest.mark.parametrize(
    "latitude, longitude",
    [
        (0, 0),
        (1, 1),
        (90, 180),
        (-90, -180),
        (45, 45),
        (-45, -45),
    ],
)
def test_init(latitude, longitude):
    weather = WeatherAPI(latitude=latitude, longitude=longitude)
    assert weather.latitude == latitude
    assert weather.longitude == longitude
    assert weather.current_date == time.strftime("%Y-%m-%d")
    assert weather._location_cache is None
    assert weather._forecast_cache is None
    assert weather._forecast_cache_date is None


def test_get_location():
    # Load the .env file
    dotenv.load_dotenv(os.path.join(TEST_DIR, "..", ".env"))
    # Get the LAT_LON_LOCATION variable
    LAT_LON_LOCATION = os.getenv("LAT_LON_LOCATION")
    # Convert the latitude and longitude to floats
    latitude, longitude = LAT_LON_LOCATION.split(",")
    latitude = float(latitude)
    longitude = float(longitude)
    # Create the WeatherAPI object
    weather = WeatherAPI(latitude=latitude, longitude=longitude)
    # Get the location data
    weather._get_location()
    # Check the location cache
    assert weather._location_cache is not None
    assert weather._location_cache == "33,35"

    # Test latitude and longitude outside of the valid range
    weather = WeatherAPI(latitude=0, longitude=0)
    # Check that warning is raised
    with pytest.warns(UserWarning):
        weather._get_location()
