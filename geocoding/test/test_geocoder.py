import pytest
from geocoding.geocoder import Geocoder
from excel_processing.excel_processor import count_dict
from geocoding.geocoder import operation_dict
from unittest.mock import patch, MagicMock
from shapely.geometry import Polygon

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


# Based on neighborhood boundaries, but extended for test purposes
zones = {
        'Recoleta': Polygon([
        (-34.59775763848938, -58.416065994430376),
        (-34.57152236217772, -58.41185706233693),
        (-34.5719757424975, -58.39287909348045),
        (-34.58905990101843, -58.38076081832795),
        (-34.59926959530766, -58.386854797200925),
        (-34.59987012647645, -58.40432134223656)
        ]),
        'Palermo': Polygon([
        (-34.59813031994899, -58.41043078579839),
        (-34.597712354404685, -58.425719980462986),
        (-34.57880882567445, -58.455621357497556),
        (-34.547262409771584, -58.43124891434665),
        (-34.55999392017572, -58.38487357100731),
        (-34.58629497803302, -58.398432951442885)
        ]),
        'Devoto': Polygon([
        (-34.610837338684554, -58.529185407271086),
        (-34.5805920535292, -58.51478084961129),
        (-34.59657530926845, -58.49661858125762),
        (-34.609290971968306, -58.50016753024627),
        (-34.62005763452868, -58.51693802069537)
        ]),
        'Retiro': Polygon([
        (-34.599168933352075, -58.386786514515904),
        (-34.59122030804602, -58.38837438224642),
        (-34.580585624507194, -58.39172177908372),
        (-34.5682533407025, -58.38326745628071),
        (-34.58153962178231, -58.35030847198172),
        (-34.598462419704575, -58.36292558314007),
        ]),
        'Saavedra': Polygon([
        (-34.569899308020865, -58.50994334180774),
        (-34.5506316955351, -58.467014705712565),
        (-34.53842365902603, -58.47611917599681),
        (-34.54901859327118, -58.50157993303969)
        ]),
        'Balvanera': Polygon([
        (-34.62053175915938, -58.412649495647976),
        (-34.59785525928151, -58.4119313168843),
        (-34.599413795127475, -58.392671068221695),
        (-34.61854378295642, -58.391561155586906)
        ])
    }

def test_classify_coordinate_outside_any_zone_is_empty():
    coordinate = (-34.91070979541186, -57.95530040583459)
    expected = []
    geocoder = Geocoder()

    assert geocoder.classify_by_zone(coordinate, zones) == expected

def test_classify_coordinate_by_zone():
    coordinate = (-34.603871342066306, -58.41100043161615)
    expected = ['Balvanera']
    geocoder = Geocoder()

    assert geocoder.classify_by_zone(coordinate, zones) == expected

def test_classify_coordinate_in_multiple_zones():
    coordinate = (-34.58869592680653, -58.38397113659946)
    expected = ['Recoleta', 'Retiro']
    geocoder = Geocoder()
    
    assert geocoder.classify_by_zone(coordinate, zones) == expected

def test_classify_coordinate_without_zones_is_empty():
    coordinate = (-34.58869592680653, -58.38397113659946)
    expected = []
    geocoder = Geocoder()

    assert geocoder.classify_by_zone(coordinate, {}) == expected


def test_classify_count_by_zone():
    operation_dict: list[operation_dict] = [
        {'name': 'Abasto',   'address': 'Av. Corrientes 3247',   'count': 2, 'coordinates': (-34.603871342066306, -58.41100043161615)},
        {'name': 'Dot',      'address': 'VEDIA 3600',            'count': 1, 'coordinates': (-34.54642280697294, -58.48787894167371)},
        {'name': 'Bullrich', 'address': 'Posadas 1245',          'count': 7, 'coordinates': (-34.58869592680653, -58.38397113659946)},
        {'name': 'Devoto',   'address': 'Quevedo 3365',          'count': 1, 'coordinates': (-34.61173697294645, -58.51780871812393)},
        {'name': 'Alcorta',  'address': 'Jerónimo Salguero 3172','count': 6, 'coordinates': (-34.57524046496525, -58.4040346824632)},
        ]

    expected: list[operation_dict] = [
        {'name': 'Abasto',   'address': 'Av. Corrientes 3247',   'count': 2, 'coordinates': (-34.603871342066306, -58.41100043161615), 'zone': ['Balvanera']},
        {'name': 'Dot',      'address': 'VEDIA 3600',            'count': 1, 'coordinates': (-34.54642280697294, -58.48787894167371), 'zone': ['Saavedra']},
        {'name': 'Bullrich', 'address': 'Posadas 1245',          'count': 7, 'coordinates': (-34.58869592680653, -58.38397113659946), 'zone': ['Recoleta', 'Retiro']},
        {'name': 'Devoto',   'address': 'Quevedo 3365',          'count': 1, 'coordinates': (-34.61173697294645, -58.51780871812393), 'zone': ['Devoto']},
        {'name': 'Alcorta',  'address': 'Jerónimo Salguero 3172','count': 6, 'coordinates': (-34.57524046496525, -58.4040346824632), 'zone': ['Palermo', 'Recoleta']},
        ]

    geocoder = Geocoder()
    result =geocoder.classfy_count_by_zone(operation_dict, zones)
    for r, e in zip(result, expected):
        assert r["name"] == e["name"]
        assert r["address"] == e["address"]
        assert r["count"] == e["count"]
        assert r["coordinates"] == e["coordinates"]
        assert "zone" in r
        assert "zone" in e
        assert sorted(r["zone"]) == sorted(e["zone"])

def test_classify_count_by_zone_without_zones():
    operation_dict: list[operation_dict] = [
        {'name': 'Abasto',   'address': 'Av. Corrientes 3247',   'count': 2, 'coordinates': (-34.603871342066306, -58.41100043161615)},
        {'name': 'Dot',      'address': 'VEDIA 3600',            'count': 1, 'coordinates': (-34.54642280697294, -58.48787894167371)}
        ]

    expected: list[operation_dict] = [
        {'name': 'Abasto',   'address': 'Av. Corrientes 3247',   'count': 2, 'coordinates': (-34.603871342066306, -58.41100043161615), 'zone': []},
        {'name': 'Dot',      'address': 'VEDIA 3600',            'count': 1, 'coordinates': (-34.54642280697294, -58.48787894167371), 'zone': []}
    ]

    geocoder = Geocoder()
    result =geocoder.classfy_count_by_zone(operation_dict, {})
    for r, e in zip(result, expected):
        assert r == e


def test_classify_count_by_zone_with_coodinate_outside_zones():
    operation_dict: list[operation_dict] = [{'name': 'Galerias', 'address': 'Av. Rivadavia 5108', 'count': 3, 'coordinates':(-34.619015354927804, -58.43780105380936)}]

    expected: list[operation_dict] = [{'name': 'Galerias', 'address': 'Av. Rivadavia 5108', 'count': 3, 'coordinates':(-34.619015354927804, -58.43780105380936), 'zone': []}]

    geocoder = Geocoder()
    result =geocoder.classfy_count_by_zone(operation_dict, zones)
    for r, e in zip(result, expected):
        assert r == e

def test_classify_count_by_zone_without_coodinates():
    operation_dict: list[operation_dict] = [{'name': 'Galerias' ,'address': 'Av. Córdoba 550','count': 9, 'coordinates': None}]

    expected: list[operation_dict] = [{'name': 'Galerias' ,'address': 'Av. Córdoba 550','count': 9, 'coordinates': None, 'zone': []}]

    geocoder = Geocoder()
    result =geocoder.classfy_count_by_zone(operation_dict, zones)
    for r, e in zip(result, expected):
        assert r == e