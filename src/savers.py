import json
import os
from abc import abstractmethod, ABC


class BaseSaver(ABC):
    @abstractmethod
    def add_aeroplane(self, aeroplane):
        pass

    @abstractmethod
    def get_data(self, criteria):
        pass


class JSONSaver(BaseSaver):
    def __init__(self, filename="planes.json"):
        self.filename = filename

    def _read_file(self):
        if not os.path.exists(self.filename):
            return []
        with open(self.filename, 'r', encoding='utf-8') as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                return []

    def add_aeroplane(self, aeroplane):
        data = self._read_file()
        new_entry = {
            "callsign": aeroplane.callsign,
            "origin_country": aeroplane.origin_country,
            "velocity": aeroplane.velocity,
            "geo_altitude": aeroplane.geo_altitude
        }
        data.append(new_entry)
        self._save_to_file(data)

    def get_data(self, criteria: dict):
        """
        Ищет данные по критериям.
        Пример criteria: {"origin_country": "Spain"}
        """
        data = self._read_file()
        results = []
        for item in data:
            if all(item.get(k) == v for k, v in criteria.items()):
                results.append(item)
        return results

    def delete_aeroplane(self, callsign):
        """Удаляет самолет из файла по его позывному."""
        data = self._read_file()
        filtered_data = [item for item in data if item.get('callsign') != callsign]

        if len(data) != len(filtered_data):
            self._save_to_file(filtered_data)
            print(f"Самолет {callsign} удален из базы.")
        else:
            print(f"Самолет {callsign} не найден.")

    def _save_to_file(self, data):
        """Вспомогательный метод для записи в файл."""
        with open(self.filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)