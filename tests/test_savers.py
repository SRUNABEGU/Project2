import os

from src.aeroplane import Aeroplane
from src.savers import JSONSaver


def test_json_saver_add_and_read(tmp_path):
    """Тестируем сохранение и чтение, используя временную папку."""
    temp_file = tmp_path / "test_planes.json"
    saver = JSONSaver(filename=str(temp_file))

    plane = Aeroplane("TEST1", "TestLand", 100, 500)
    saver.add_aeroplane(plane)

    data = saver._read_file()
    assert len(data) == 1
    assert data[0]['callsign'] == "TEST1"


def test_json_saver_delete(tmp_path):
    f = tmp_path / "test.json"
    saver = JSONSaver(str(f))
    plane = Aeroplane("DEL123", "Test", 100, 1000)

    saver.add_aeroplane(plane)

    saver.delete_aeroplane("DEL123")
    assert len(saver._read_file()) == 0

    saver.delete_aeroplane("NONEXISTENT")


def test_json_saver_get_data(tmp_path):
    f = tmp_path / "test.json"
    saver = JSONSaver(str(f))
    saver.add_aeroplane(Aeroplane("FIND_ME", "TargetCountry", 100, 1000))

    results = saver.get_data({"origin_country": "TargetCountry"})
    assert len(results) == 1
    assert results[0]["callsign"] == "FIND_ME"