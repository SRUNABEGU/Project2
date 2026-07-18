from unittest.mock import patch, MagicMock
from src.abc_api import AircraftAPI


@patch('requests.get')
def test_get_country_bounds(mock_get):
    """Тестируем получение координат страны без интернета."""
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = [{'boundingbox': ['50.0', '52.0', '19.0', '21.0']}]
    mock_get.return_value = mock_response

    api = AircraftAPI()
    bounds = api._get_country_bounds("Poland")

    assert bounds == [50.0, 52.0, 19.0, 21.0]
    mock_get.assert_called_once()


@patch('src.abc_api.AircraftAPI._get_country_bounds')
@patch('requests.get')
def test_get_aeroplanes_empty_response(mock_get, mock_bounds):
    api = AircraftAPI()
    mock_bounds.return_value = [0, 1, 0, 1]

    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"states": None}
    mock_get.return_value = mock_response

    assert api.get_aeroplanes("AnyCountry") == []