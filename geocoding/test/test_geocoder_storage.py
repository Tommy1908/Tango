from geocoding.geocoder_storage import Geocoder_storage
from geocoding.geocoder import Geocoder
from schemas import count_dict, operation_dict
from unittest.mock import Mock, patch
from shapely.geometry import Polygon
import json
import pytest

def test_storage_saves_data(tmp_path):
    info: list[operation_dict] = [
        {'name': 'BA ABASTO HOTEL - Hotel',    'address': 'Jean Jaures 896', 'count': 2,   'coordinates': (1, 1)},
        {'name': 'BELIEVE - Hotel',            'address': 'CHILE 80',        'count': 10,  'coordinates': (0, 0)},
        {'name': 'DOLMEN - Hotel',             'address': 'SUIPACHA 1079',   'count': 6,  'coordinates': (-1, -1)},
        ]
    dir = tmp_path / "geocoding_test_tmp"
    dir.mkdir()
    file_path = dir / "geocoding.json"

    storage = Geocoder_storage()
    storage._save_coords(info, file_path)

    with open(file_path, "r", encoding="utf-8") as f:
        saved_data = json.load(f)
        
        assert len(saved_data) == len(info)
    
        for r, e in zip(saved_data, info):
            assert r["name"] == e["name"]
            assert r["address"] == e["address"]
            assert tuple(r["coordinates"]) == e["coordinates"]

def test_storage_only_adds_data(tmp_path):

    info: list[operation_dict] = [
        {'name': 'BA ABASTO HOTEL - Hotel',    'address': 'Jean Jaures 896', 'count': 2,   'coordinates': (1, 1)},
        {'name': 'BELIEVE - Hotel',            'address': 'CHILE 80',        'count': 10,  'coordinates': (0, 0)},
        {'name': 'DOLMEN - Hotel',             'address': 'SUIPACHA 1079',   'count': 6,  'coordinates': (-1, -1)},
        ]
    new_info: list[operation_dict] = [
        {'name': 'AQ TAILORED SUITES - Hotel', 'address': 'MONTEVIDEO 937',  'count': 2,   'coordinates': (2, 2)},
        {'name': 'BA ABASTO HOTEL - Hotel',    'address': 'Jean Jaures 896', 'count': 2,   'coordinates': (16, 16)},
        {'name': 'BROADWAY - Hotel',           'address': 'CORRIENTES 1173', 'count': 2,  'coordinates': (5, 5)},
        {'name': 'DOLMEN - Hotel',             'address': 'SUIPACHA 1079',   'count': 6,  'coordinates': (16, 16)},
        ]
    expected: list[operation_dict] = [
        {'name': 'AQ TAILORED SUITES - Hotel', 'address': 'MONTEVIDEO 937',  'count': 2,   'coordinates': (2, 2)},
        {'name': 'BA ABASTO HOTEL - Hotel',    'address': 'Jean Jaures 896', 'count': 2,   'coordinates': (1, 1)},
        {'name': 'BELIEVE - Hotel',            'address': 'CHILE 80',        'count': 10,  'coordinates': (0, 0)},
        {'name': 'BROADWAY - Hotel',           'address': 'CORRIENTES 1173', 'count': 2,  'coordinates': (5, 5)},
        {'name': 'DOLMEN - Hotel',             'address': 'SUIPACHA 1079',   'count': 6,  'coordinates': (-1, -1)},
        ]

    dir = tmp_path / "geocoding_test_tmp"
    dir.mkdir()
    file_path = dir / "geocoding.json"

    storage = Geocoder_storage()
    storage._save_coords(info, file_path)

    storage._save_coords(new_info, file_path)

    with open(file_path, "r", encoding="utf-8") as f:
        saved_data = json.load(f)
        
        assert len(saved_data) == len(expected)
        saved_data.sort(key=lambda x: x['name'])
        expected.sort(key=lambda x: x['name'])
        for r, e in zip(saved_data, expected):
            assert r["name"] == e["name"]
            assert r["address"] == e["address"]
            assert tuple(r["coordinates"]) == e["coordinates"]

def test_storage_handles_empty_file(tmp_path):
    dir = tmp_path / "geocoding_test_tmp"
    dir.mkdir()
    file_path = dir / "empty.json"
    file_path.write_text("")

    storage = Geocoder_storage(file_path)
    storage._save_coords([], file_path)

    with open(file_path, "r") as f:
        saved_data = json.load(f)
        assert saved_data == []


def test_get_saved_coords_returns_name_to_coords_mapping(tmp_path):
    info: list[operation_dict] = [
        {'name': 'BA ABASTO HOTEL - Hotel', 'address': 'Jean Jaures 896', 'count': 2, 'coordinates': (1, 1)},
        {'name': 'BELIEVE - Hotel',         'address': 'CHILE 80',        'count': 10, 'coordinates': (0, 0)},
    ]
    file_path = tmp_path / "auto.json"
    storage = Geocoder_storage(automatic_path=file_path)
    storage._save_coords(info, file_path)

    result = storage.get_saved_coords()
    assert result == {
        'BA ABASTO HOTEL - Hotel': (1, 1),
        'BELIEVE - Hotel': (0, 0),
    }


def test_get_saved_coords_merges_auto_and_manual(tmp_path):
    auto_info: list[operation_dict] = [
        {'name': 'BA ABASTO HOTEL - Hotel', 'address': 'Jean Jaures 896', 'count': 2, 'coordinates': (1, 1)},
        {'name': 'BELIEVE - Hotel',         'address': 'CHILE 80',        'count': 10, 'coordinates': (0, 0)},
    ]
    manual_info: list[operation_dict] = [
        {'name': 'BA ABASTO HOTEL - Hotel', 'address': 'Jean Jaures 896', 'count': 2, 'coordinates': (99, 99)},
    ]
    auto_path = tmp_path / "auto.json"
    manual_path = tmp_path / "manual.json"
    storage = Geocoder_storage(automatic_path=auto_path, manual_path=manual_path)
    storage._save_coords(auto_info, auto_path)
    storage._save_coords(manual_info, manual_path)

    result = storage.get_saved_coords()
    assert result['BA ABASTO HOTEL - Hotel'] == (99, 99)
    assert result['BELIEVE - Hotel'] == (0, 0)


def test_get_saved_coords_returns_empty_when_no_files(tmp_path):
    storage = Geocoder_storage(
        automatic_path=tmp_path / "nonexistent_auto.json",
        manual_path=tmp_path / "nonexistent_manual.json"
    )
    result = storage.get_saved_coords()
    assert result == {}


def test_save_persists_operation_dict(tmp_path):
    result: list[operation_dict] = [
        {'name': 'Hotel A', 'address': 'Calle 1', 'count': 3, 'coordinates': (-34.6, -58.38)},
        {'name': 'Hotel B', 'address': 'Calle 2', 'count': 5, 'coordinates': (-34.61, -58.39)},
    ]
    file_path = tmp_path / "auto.json"
    storage = Geocoder_storage(automatic_path=file_path)
    storage.save(result)

    with open(file_path, "r", encoding="utf-8") as f:
        saved = json.load(f)
    assert len(saved) == 2
    assert saved[0]['name'] == 'Hotel A'
    assert saved[1]['name'] == 'Hotel B'
    assert 'count' not in saved[0]
    assert 'count' not in saved[1]


def test_save_does_not_overwrite_existing_names(tmp_path):
    first: list[operation_dict] = [
        {'name': 'Hotel A', 'address': 'Calle 1', 'count': 3, 'coordinates': (1, 1)},
    ]
    second: list[operation_dict] = [
        {'name': 'Hotel A', 'address': 'Calle 1', 'count': 3, 'coordinates': (99, 99)},
    ]
    file_path = tmp_path / "auto.json"
    storage = Geocoder_storage(automatic_path=file_path)
    storage.save(first)
    storage.save(second)

    with open(file_path, "r", encoding="utf-8") as f:
        saved = json.load(f)
    assert len(saved) == 1
    assert tuple(saved[0]['coordinates']) == (1, 1)


@patch("geocoding.geocoder.Photon.geocode")
def test_geocode_and_save_full_pipeline(mock_geocode, tmp_path):
    mock_geocode.return_value = Mock(latitude=-34.60, longitude=-58.38)

    count: list[count_dict] = [
        {'name': 'Hotel A', 'address': 'Calle 1', 'count': 3},
        {'name': 'Hotel B', 'address': 'Calle 2', 'count': 5},
    ]
    file_path = tmp_path / "auto.json"
    storage = Geocoder_storage(automatic_path=file_path)
    geocoder = Geocoder()

    result = storage.geocode_and_save(count, geocoder)

    assert len(result) == 2
    assert result[0]['name'] == 'Hotel A'
    assert result[0]['coordinates'] is not None
    assert file_path.exists()

    with open(file_path, "r", encoding="utf-8") as f:
        saved = json.load(f)
    assert len(saved) == 2


@patch("geocoding.geocoder.Photon.geocode")
def test_geocode_and_save_with_manual_overrides(mock_geocode, tmp_path):
    mock_geocode.return_value = Mock(latitude=-34.60, longitude=-58.38)

    manual_info = [
        {'name': 'Hotel A', 'address': 'Calle 1', 'coordinates': (99, 99)},
    ]

    manual_path = tmp_path / "manual.json"
    automatic_path = tmp_path / "auto.json"
    storage = Geocoder_storage(automatic_path=automatic_path, manual_path=manual_path)

    storage._save_coords(manual_info, manual_path)

    count: list[count_dict] = [
        {'name': 'Hotel A', 'address': 'Calle 1', 'count': 3},
        {'name': 'Hotel B', 'address': 'Calle 2', 'count': 5},
    ]
    geocoder = Geocoder()
    result = storage.geocode_and_save(count, geocoder)

    hotel_A = next(r for r in result if r['name'] == 'Hotel A')
    assert hotel_A['coordinates'] == (99, 99)
    mock_geocode.assert_called_once()
