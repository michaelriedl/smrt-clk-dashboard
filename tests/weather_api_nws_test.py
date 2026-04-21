import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

import dotenv
import pytest

from smrtclk.weather.weather_api_nws import WeatherAPINWS


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

def _make_period(
    number=1,
    name="Tonight",
    is_daytime=False,
    temperature=35,
    temp_unit="F",
    precip=20,
    start_time="2026-04-20T18:00:00-04:00",
):
    return {
        "number": number,
        "name": name,
        "startTime": start_time,
        "isDaytime": is_daytime,
        "temperature": temperature,
        "temperatureUnit": temp_unit,
        "probabilityOfPrecipitation": {"unitCode": "wmoUnit:percent", "value": precip},
    }


def _make_raw(periods):
    return {"properties": {"periods": periods}}


@pytest.fixture
def nws():
    return WeatherAPINWS(latitude=40.7128, longitude=-74.0060)

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
    assert weather._location_cache is None
    assert weather._weather_cache is None
    assert weather._cache_timestamp is None


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
        assert weather._location_cache is None
        assert weather._weather_cache is None
        assert weather._cache_timestamp is None


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
    # Grid coordinates can shift between NWS API updates; just verify format
    import re
    assert re.match(r"^[A-Z]+/\d+,\d+$", weather._location_cache), (
        f"Unexpected location format: {weather._location_cache!r}"
    )


def test_get_current_weather():
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
    # Get the current weather data
    result = weather.get_current_weather()
    # Check the result
    assert result is not None
    assert "status" in result
    assert result["status"] == "ok"
    # Check the cache was populated
    assert weather._weather_cache is not None
    assert weather._cache_timestamp is not None

    # Test getting weather with cached data
    cached_result = weather.get_current_weather()
    assert cached_result["status"] == "cached"

    # Test latitude and longitude outside of the valid range
    weather = WeatherAPINWS(latitude=0, longitude=0)
    # Check that error status is returned for invalid coordinates
    result = weather.get_current_weather()
    assert result["status"] == "error"
    assert "error_message" in result


# ---------------------------------------------------------------------------
# _parse_weather_data unit tests (no network required)
# ---------------------------------------------------------------------------

def test_parse_raises_on_empty_periods(nws):
    with pytest.raises(ValueError, match="No forecast periods"):
        nws._parse_weather_data(_make_raw([]))


def test_parse_raises_on_missing_periods_key(nws):
    with pytest.raises(ValueError, match="No forecast periods"):
        nws._parse_weather_data({"properties": {}})


def test_parse_temperature_fahrenheit(nws):
    periods = [
        _make_period(1, "Tonight", False, temperature=35, temp_unit="F", precip=0),
        _make_period(2, "Tuesday", True, temperature=53, temp_unit="F", precip=5),
    ]
    result = nws._parse_weather_data(_make_raw(periods))
    assert result["temperature"] == 35.0
    assert result["temperature_max"] == 53.0
    assert result["temperature_min"] == 35.0


def test_parse_temperature_celsius_converted(nws):
    periods = [
        _make_period(1, "Tonight", False, temperature=0, temp_unit="C", precip=0),
        _make_period(2, "Tuesday", True, temperature=10, temp_unit="C", precip=0),
    ]
    result = nws._parse_weather_data(_make_raw(periods))
    assert result["temperature"] == 32.0
    assert result["temperature_max"] == 50.0


def test_parse_precipitation_values(nws):
    periods = [
        _make_period(1, "Tonight", False, temperature=35, precip=20),
        _make_period(2, "Tuesday", True, temperature=53, precip=5),
        _make_period(3, "Tuesday Night", False, temperature=43, precip=40),
        _make_period(4, "Wednesday", True, temperature=60, precip=10),
    ]
    result = nws._parse_weather_data(_make_raw(periods))
    assert result["precipitation"] == 20
    assert result["precipitation_min"] == 5
    assert result["precipitation_max"] == 40


def test_parse_null_precipitation_treated_as_zero(nws):
    period = _make_period(1, "Tonight", False, temperature=35, precip=None)
    period["probabilityOfPrecipitation"]["value"] = None
    result = nws._parse_weather_data(_make_raw([period]))
    assert result["precipitation"] == 0
    assert result["precipitation_min"] == 0
    assert result["precipitation_max"] == 0


def test_parse_sunrise_sunset_format(nws):
    periods = [_make_period(1, "Tonight", False, temperature=35, precip=0)]
    result = nws._parse_weather_data(_make_raw(periods))
    for key in ("sunrise", "sunset"):
        val = result[key]
        assert len(val) == 5, f"{key} should be HH:MM, got {val!r}"
        assert val[2] == ":", f"{key} missing colon, got {val!r}"
        h, m = int(val[:2]), int(val[3:])
        assert 0 <= h <= 23
        assert 0 <= m <= 59


def test_parse_sunrise_before_sunset(nws):
    periods = [_make_period(1, "Tonight", False, temperature=35, precip=0)]
    result = nws._parse_weather_data(_make_raw(periods))
    assert result["sunrise"] < result["sunset"]


def test_parse_utc_offset_positive(nws):
    assert nws._parse_utc_offset("2026-07-01T06:00:00+05:30") == pytest.approx(5.5)


def test_parse_utc_offset_negative(nws):
    assert nws._parse_utc_offset("2026-04-20T18:00:00-04:00") == pytest.approx(-4.0)


def test_parse_utc_offset_bad_input_falls_back(nws):
    offset = nws._parse_utc_offset("not-a-timestamp")
    assert isinstance(offset, float)


def test_parse_single_daytime_period(nws):
    """When only one daytime period exists, min and max should both reflect it."""
    periods = [_make_period(1, "Today", True, temperature=70, precip=10)]
    result = nws._parse_weather_data(_make_raw(periods))
    assert result["temperature"] == 70.0
    assert result["temperature_max"] == 70.0
    assert result["temperature_min"] == 70.0


# ---------------------------------------------------------------------------
# Integration: get_current_weather returns all required fields
# ---------------------------------------------------------------------------

def test_get_current_weather_all_fields():
    dotenv.load_dotenv(os.path.join(TEST_DIR, "..", ".env"))
    LAT_LON_LOCATION = os.getenv("LAT_LON_LOCATION")
    latitude, longitude = LAT_LON_LOCATION.split(",")
    weather = WeatherAPINWS(latitude=float(latitude), longitude=float(longitude))
    result = weather.get_current_weather()
    assert result["status"] == "ok"
    required = [
        "temperature", "temperature_min", "temperature_max",
        "precipitation", "precipitation_min", "precipitation_max",
        "sunrise", "sunset",
    ]
    for field in required:
        assert field in result, f"Missing field: {field}"
