import pytest
from src.aeroplane import Aeroplane

def test_aeroplane_init():
    """Проверяем создание объекта и валидацию данных."""
    plane = Aeroplane("AFR123", "France", "250.5", "10000")
    assert plane.callsign == "AFR123"
    assert plane.velocity == 250.5
    assert plane.geo_altitude == 10000

def test_aeroplane_invalid_data():
    """Проверяем, что валидатор справляется с некорректными данными."""
    plane = Aeroplane("ERR", "Unknown", "invalid", None)
    assert plane.velocity == 0
    assert plane.geo_altitude == 0

def test_aeroplane_comparison():
    """Проверяем работу сравнения (магический метод __lt__)."""
    low_plane = Aeroplane("LOW", "Country", 100, 1000)
    high_plane = Aeroplane("HIGH", "Country", 100, 5000)
    assert low_plane < high_plane
    assert high_plane > low_plane

def test_cast_to_object_list():
    # Имитируем ответ от API
    mock_raw_data = [
        ["icao24", "CALL123", "Origin", 1712910000, 1712910000, 0, 0, 10000, False, 250, 0, 0, None, 10000, "1234", False, 0]
    ]
    planes = Aeroplane.cast_to_object_list(mock_raw_data)
    assert len(planes) == 1
    assert planes[0].callsign == "CALL123"
    assert planes[0].geo_altitude == 10000