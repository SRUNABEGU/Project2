class Aeroplane:
    """Класс, представляющий воздушное судно."""

    def __init__(self, icao24, callsign, origin_country, velocity, geo_altitude):
        self.icao24 = icao24.strip() if icao24 else "Unknown"
        self.callsign = callsign.strip() if callsign else "Unknown"
        self.origin_country = origin_country
        self.__velocity = self._validate_positive(velocity)
        self.__geo_altitude = self._validate_positive(geo_altitude)

    @staticmethod
    def _validate_positive(value):
        """Простейшая валидация данных."""
        try:
            val = float(value)
            return val if val >= 0 else 0
        except (TypeError, ValueError):
            return 0

    @property
    def velocity(self):
        return self.__velocity

    @property
    def geo_altitude(self):
        return self.__geo_altitude

    def __lt__(self, other):
        return self.__geo_altitude < other.__geo_altitude

    def __repr__(self):
        return f"Plane({self.callsign}, Country: {self.origin_country}, Alt: {self.__geo_altitude}m, Spd: {self.__velocity}m/s)"

    @classmethod
    def cast_to_object_list(cls, raw_data):
        """Преобразует сырые данные из API в список объектов Aeroplane."""
        objects = []
        for item in raw_data:
            # item[0] - это icao24, item[1] - callsign, item[9] - velocity, item[7] - geo_altitude
            objects.append(cls(item[0], item[1], item[2], item[9], item[7]))
        return objects