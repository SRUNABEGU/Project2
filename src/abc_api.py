import requests
from abc import ABC, abstractmethod


class BaseAPI(ABC):
    @abstractmethod
    def get_aeroplanes(self, country_name):
        pass


class AircraftAPI(BaseAPI):
    def __init__(self):
        self.nominatim_url = "https://nominatim.openstreetmap.org/search"
        self.opensky_url = "https://opensky-network.org/api/states/all"

    def _get_country_bounds(self, country_name):
        """Получает координаты границ страны (boundingbox)."""
        params = {
            'country': country_name,
            'format': 'json',
            'limit': 1
        }
        headers = {'User-Agent': 'CourseWorkApp/1.0'}
        response = requests.get(self.nominatim_url, params=params, headers=headers)

        if response.status_code == 200 and response.json():
            data = response.json()[0]
            return [float(x) for x in data['boundingbox']]
        return None

    def get_aeroplanes(self, country_name):
        bounds = self._get_country_bounds(country_name)
        if not bounds:
            print(f"Страна {country_name} не найдена.")
            return []

        params = {
            'lamin': bounds[0],
            'lamax': bounds[1],
            'lomin': bounds[2],
            'lomax': bounds[3]
        }

        try:
            # Добавляем timeout=10 секунд, чтобы скрипт не висел вечно
            response = requests.get(self.opensky_url, params=params, timeout=10)
            if response.status_code == 200:
                states = response.json().get('states')
                return states if states else []
            else:
                print(f"[Предупреждение] OpenSky вернул код {response.status_code} для {country_name}")
        except requests.exceptions.RequestException:
            # Если сервер лег или таймаут — не падаем, а вежливо пропускаем
            print(f"[Ошибка сети] OpenSky не ответил вовремя для {country_name}. Пропускаем...")

        return []