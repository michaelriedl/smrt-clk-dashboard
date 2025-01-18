import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

import time

import dotenv
import pytest

from smrtclk.weather.weather_api_nws import WeatherAPINWS

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
    weather = WeatherAPINWS(latitude=latitude, longitude=longitude)
    assert weather.latitude == latitude
    assert weather.longitude == longitude
    assert weather.current_date == time.strftime("%Y-%m-%d")
    assert weather._location_cache is None
    assert weather._forecast_cache is None
    assert weather._forecast_cache_date is None


@pytest.mark.parametrize(
    "latitude, longitude",
    [
        ("0", 0),
        (0, "0"),
        (0.0, 0),
        (0, 0.0),
        (0.0, 0.0),
    ],
)
def test_init_type_error(latitude, longitude):
    if isinstance(latitude, str) or isinstance(longitude, str):
        with pytest.raises(TypeError):
            WeatherAPINWS(latitude=latitude, longitude=longitude)
    else:
        weather = WeatherAPINWS(latitude=latitude, longitude=longitude)
        assert weather.latitude == latitude
        assert weather.longitude == longitude
        assert weather.current_date == time.strftime("%Y-%m-%d")
        assert weather._location_cache is None
        assert weather._forecast_cache is None
        assert weather._forecast_cache_date is None


def test_setters():
    # Load the .env file
    dotenv.load_dotenv(os.path.join(TEST_DIR, "..", ".env"))
    # Get the LAT_LON_LOCATION variable
    LAT_LON_LOCATION = os.getenv("LAT_LON_LOCATION")
    # Convert the latitude and longitude to floats
    latitude, longitude = LAT_LON_LOCATION.split(",")
    latitude = float(latitude)
    longitude = float(longitude)
    weather = WeatherAPINWS(latitude=latitude, longitude=longitude)
    weather._get_location()
    assert weather._location_cache is not None
    # Test setting latitude
    weather.latitude = 1
    assert weather.latitude == 1
    assert weather._location_cache is None
    # Reset the location cache
    weather.latitude = latitude
    weather._get_location()
    # Test setting longitude
    weather.longitude = 1
    assert weather.longitude == 1
    assert weather._location_cache is None

    # Test setting latitude outside of the valid range
    with pytest.raises(ValueError):
        weather.latitude = 91
    # Test setting longitude outside of the valid range
    with pytest.raises(ValueError):
        weather.longitude = 181

    # Test setting latitude to a string
    with pytest.raises(TypeError):
        weather.latitude = "1"
    # Test setting longitude to a string
    with pytest.raises(TypeError):
        weather.longitude = "1"


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
    weather = WeatherAPINWS(latitude=latitude, longitude=longitude)
    # Get the location data
    weather._get_location()
    # Check the location cache
    assert weather._location_cache is not None
    assert weather._location_cache == "OKX/33,35"

    # Test latitude and longitude outside of the valid range
    weather = WeatherAPINWS(latitude=0, longitude=0)
    # Check that warning is raised
    with pytest.warns(UserWarning):
        weather._get_location()


def test_get_forecast():
    # Load the .env file
    dotenv.load_dotenv(os.path.join(TEST_DIR, "..", ".env"))
    # Get the LAT_LON_LOCATION variable
    LAT_LON_LOCATION = os.getenv("LAT_LON_LOCATION")
    # Convert the latitude and longitude to floats
    latitude, longitude = LAT_LON_LOCATION.split(",")
    latitude = float(latitude)
    longitude = float(longitude)
    # Create the WeatherAPI object
    weather = WeatherAPINWS(latitude=latitude, longitude=longitude)
    # Get the forecast data
    weather._get_forecast()
    # Check the forecast cache
    assert weather._forecast_cache is not None
    assert weather._forecast_cache_date == time.strftime("%Y-%m-%d-%H-%M-%S")

    # Test latitude and longitude outside of the valid range
    weather = WeatherAPINWS(latitude=0, longitude=0)
    # Check that warning is raised
    with pytest.warns(UserWarning):
        weather._get_forecast()
