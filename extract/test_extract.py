import pytest
from unittest.mock import MagicMock, patch
import os
from datetime import datetime
from moto import mock_s3

from extract import get_flights_for_all_celebs, get_flight_params, get_celeb_json, get_current_flight_for_icao


def test_celebs_have_expected_plane_info(celeb_planes_data):
    """"""

    for celeb_plane in celeb_planes_data:
        assert "icao_hex" in celeb_plane and "tail_number" in celeb_plane


@patch("extract.get_current_flight_for_icao")
def test_get_flights_for_celebs(mocked_flight_info, celeb_planes_data):
    """Checks that get flights for celebs function returns a list where each item is
    a dict corresponding to a celebrity in the input."""

    mocked_flight_info.return_value = {}
    result = get_flights_for_all_celebs(celeb_planes_data)
    assert isinstance(result, list) and len(celeb_planes_data) == len(result)


def test_get_flight_params_raises_keyerror():
    """"""

    with pytest.raises(KeyError) as err:
        data = {}
        get_flight_params(data)

    assert err.match('ac')


def test_get_flight_params_unix_conversion():
    """"""

    data = {"ac": [{}], "now": 1}
    assert get_flight_params(data)["time_input"] == datetime(1970, 1, 1, 0, 0, 0, 1000)


@patch("boto3.resource")
def test_get_celeb_json_from_s3(mocked_s3):
    """"""
    os.environ["S3_BUCKET_NAME"] = "test_bucket"
    os.environ["CELEB_INFO"] = "test"

    mock_bucket = mocked_s3.return_value.Object
    mock_readable = MagicMock()
    mock_readable.read.return_value = '{"please": "work"}'
    mock_bucket.return_value.get.return_value = {"Body": mock_readable}
    data = get_celeb_json()

    mock_bucket.assert_called()
    assert data == {"please": "work"}


@patch("requests.get")
def test_api_call(mock_request):
    """"""
    os.environ["RAPIDAPI_KEY"] = "shhhh"
    os.environ["RAPIDAPI_HOST"] = "it's secret"

    mock_request.return_value.json.return_value = "Success"
    data = get_current_flight_for_icao("6zerozerozero")

    mock_request.assert_called()
    assert data == "Success"
