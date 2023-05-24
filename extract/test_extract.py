import pytest
from unittest.mock import MagicMock, patch

from extract import get_flights_for_all_celebs, get_flight_params


def test_celebs_have_expected_plane_info(celeb_planes_data):
    """"""
    for celeb_plane in celeb_planes_data:
        assert "icao_hex" in celeb_plane and "tail_number" in celeb_plane


@patch("extract.get_current_flight_for_icao")
def test_get_flights_for_celebs(mocked_flight_info, celeb_planes_data):
    """"""
    mocked_flight_info.return_value = {}
    result = get_flights_for_all_celebs(celeb_planes_data)
    assert isinstance(result, list) and len(celeb_planes_data) == len(result)


def test_get_flight_params():
    """"""
    with pytest.raises(KeyError) as err:
        data = {}
        get_flight_params(data)

    assert err.match('ac')