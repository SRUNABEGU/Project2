import psycopg2
from psycopg2.extras import RealDictCursor

class DBManager:
    """Класс для работы с базой данных PostgreSQL и анализа данных о полетах."""

    def __init__(self, db_config: dict):
        """Инициализирует подключение к БД."""
        self.conn = psycopg2.connect(**db_config)
        self.create_tables()

    def create_tables(self):
        """Создает таблицы для стран и самолетов, если они не существуют."""
        with self.conn.cursor() as cur:
            # Таблица стран
            cur.execute("""
                CREATE TABLE IF NOT EXISTS countries (
                    country_id SERIAL PRIMARY KEY,
                    name VARCHAR(100) UNIQUE NOT NULL,
                    lat_min NUMERIC, lat_max NUMERIC,
                    lon_min NUMERIC, lon_max NUMERIC
                );
            """)
            # Таблица самолетов (со ссылкой на страну, над которой летят)
            cur.execute("""
                CREATE TABLE IF NOT EXISTS aeroplanes (
                    icao24 VARCHAR(10) PRIMARY KEY,
                    callsign VARCHAR(20),
                    origin_country VARCHAR(100),
                    velocity NUMERIC,
                    geo_altitude NUMERIC,
                    country_id INT REFERENCES countries(country_id) ON DELETE CASCADE
                );
            """)
        self.conn.commit()

    def save_country(self, name, bounds) -> int:
        """Сохраняет страну и возвращает ее country_id."""
        with self.conn.cursor() as cur:
            cur.execute("""
                INSERT INTO countries (name, lat_min, lat_max, lon_min, lon_max)
                VALUES (%s, %s, %s, %s, %s)
                ON CONFLICT (name) DO UPDATE SET name=EXCLUDED.name
                RETURNING country_id;
            """, (name, bounds[0], bounds[1], bounds[2], bounds[3]))
            country_id = cur.fetchone()[0]
        self.conn.commit()
        return country_id

    def save_aeroplane(self, plane, country_id):
        """Сохраняет или обновляет данные о самолете."""
        with self.conn.cursor() as cur:
            cur.execute("""
                INSERT INTO aeroplanes (icao24, callsign, origin_country, velocity, geo_altitude, country_id)
                VALUES (%s, %s, %s, %s, %s, %s)
                ON CONFLICT (icao24) DO UPDATE SET 
                    callsign=EXCLUDED.callsign,
                    velocity=EXCLUDED.velocity,
                    geo_altitude=EXCLUDED.geo_altitude,
                    country_id=EXCLUDED.country_id;
            """, (plane.icao24, plane.callsign, plane.origin_country, plane.velocity, plane.geo_altitude, country_id))
        self.conn.commit()

    # --- МЕТОДЫ ИЗ ЗАДАНИЯ ---

    def get_countries_and_aeroplanes_count(self):
        """1. Получает список всех стран и количество самолетов в их воздушных пространствах."""
        query = """
            SELECT c.name, COUNT(a.icao24) as aeroplane_count
            FROM countries c
            LEFT JOIN aeroplanes a ON c.country_id = a.country_id
            GROUP BY c.name;
        """
        with self.conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(query)
            return cur.fetchall()

    def get_all_aeroplanes(self):
        """2. Получает список всех воздушных судов."""
        query = "SELECT * FROM aeroplanes;"
        with self.conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(query)
            return cur.fetchall()

    def get_avg_speed(self) -> float:
        """3. Получает среднюю скорость по самолетам."""
        query = "SELECT AVG(velocity) FROM aeroplanes;"
        with self.conn.cursor() as cur:
            cur.execute(query)
            res = cur.fetchone()[0]
            return float(res) if res else 0.0

    def get_aeroplanes_with_higher_speed(self):
        """4. Получает список всех самолетов, у которых скорость выше средней."""
        query = """
            SELECT * FROM aeroplanes 
            WHERE velocity > (SELECT AVG(velocity) FROM aeroplanes);
        """
        with self.conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(query)
            return cur.fetchall()

    def get_aeroplanes_with_keyword(self, keyword: str):
        """5. Получает список всех самолетов, в позывном которых содержатся переданные символы."""
        query = "SELECT * FROM aeroplanes WHERE callsign LIKE %s;"
        with self.conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(query, (f"%{keyword}%",))
            return cur.fetchall()

    def clear_aeroplanes(self):
        """Очищает таблицу самолетов перед новым запуском (чтобы данные были актуальными)."""
        with self.conn.cursor() as cur:
            cur.execute("TRUNCATE TABLE aeroplanes;")
        self.conn.commit()

    def close(self):
        """Закрывает соединение с БД."""
        self.conn.close()