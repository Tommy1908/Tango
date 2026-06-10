import pytest
from geocoding.geocoder import Geocoder
from excel_processing.excel_processor import count_dict
from geocoding.geocoder import operation_dict
from unittest.mock import patch, MagicMock

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


@patch("geocoding.geocoder.Photon.geocode")
def test_geocode_address_not_found(mock_geocode):
    mock_geocode.return_value = None

    geocoder = Geocoder()
    assert geocoder.geocode_address("FAKE ADDR") is None

@patch("geocoding.geocoder.Photon.geocode")
def test_geocode_api_error(mock_geocode):
    mock_geocode.side_effect = Exception("Timeout total")

    geocoder = Geocoder()
    assert geocoder.geocode_address("MONTEVIDEO 937") is None


def test_geocoding_from_count():

    count: list[count_dict] = [
        {'name': 'AQ TAILORED SUITES - Hotel', 'address': 'MONTEVIDEO 937',  'count': 2},
        {'name': 'BA ABASTO HOTEL - Hotel',    'address': 'Jean Jaures 896', 'count': 2},
        {'name': 'BELIEVE - Hotel',            'address': 'CHILE 80',        'count': 10},
        {'name': 'BROADWAY - Hotel',           'address': 'CORRIENTES 1173', 'count': 2},
        {'name': 'DOLMEN - Hotel',             'address': 'SUIPACHA 1079',   'count': 6},
        {'name': 'EL CONQUISTADOR - Hotel',    'address': 'SUIPACHA 948',    'count': 2}
        ]
    expected_count: list[operation_dict] = [
        {'name': 'AQ TAILORED SUITES - Hotel', 'address': 'MONTEVIDEO 937',  'count': 2,   'coordinates': (-34.59797807863827, -58.38956811921236)},
        {'name': 'BA ABASTO HOTEL - Hotel',    'address': 'Jean Jaures 896', 'count': 2,   'coordinates': (-34.599892671264975, -58.40748444915101)},
        {'name': 'BELIEVE - Hotel',            'address': 'CHILE 80',        'count': 10,  'coordinates': (-34.61575980925757, -58.36735230242128)},
        {'name': 'BROADWAY - Hotel',           'address': 'CORRIENTES 1173', 'count': 2,  'coordinates': (-34.60367008315645, -58.38332589438214)},
        {'name': 'DOLMEN - Hotel',             'address': 'SUIPACHA 1079',   'count': 6,  'coordinates': (-34.59560372808062, -58.379906182095084)},
        {'name': 'EL CONQUISTADOR - Hotel',    'address': 'SUIPACHA 948',    'count': 2,  'coordinates': (-34.59706125395073, -58.37998639023662)},
        ]

    geocoder = Geocoder()
    result =geocoder.geocode_count(count)

    for r, e in zip(result, expected_count):
        assert r["name"] == e["name"]
        assert r["address"] == e["address"]
        assert r["count"] == e["count"]
        assert r["coordinates"] == pytest.approx(
            e["coordinates"],
            abs=2.5e-4
        )
