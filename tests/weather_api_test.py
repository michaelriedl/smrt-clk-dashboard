import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

import time

import pytest

from smrtclk.weather.weather_api import WeatherAPI


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
