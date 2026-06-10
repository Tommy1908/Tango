import pytest
from geocoding.geocoder import Geocoder


def test_geocoding_address():
    address = "ARENALES 1210"
    expected = (-34.59452737273685, -58.38457436448243)
    geocoder = Geocoder()

    #assert geocoder.geocode_address(address) == expected
    assert geocoder.geocode_address(address) == pytest.approx(expected, abs=2.5e-4)

    address = "MONTEVIDEO 937"
    expected = (-34.59797807863827, -58.38956811921236)
    #assert geocoder.geocode_address(address) == expected
    assert geocoder.geocode_address(address) == pytest.approx(expected, abs=2.5e-4)
