import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

import time

from smrtclk.weather.weather_api import WeatherAPI


def test_init():
    weather = WeatherAPI()
    assert weather.current_date == time.strftime("%Y-%m-%d")
    assert weather._location_cache is None
    assert weather._forecast_cache is None
