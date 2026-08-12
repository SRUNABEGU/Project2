from src.abc_api import AircraftAPI
from src.aeroplane import Aeroplane
from src.db_manager import DBManager

# Настройки подключения к твоей базе данных PostgreSQL
DB_CONFIG = {
    "host": "localhost",
    "port": "5432",
    "database": "sky_tracker",
    "user": "postgres",
    "password": "your_password"
}

REQUIRED_COUNTRIES = [
    "Germany", "Poland", "Italy", "Netherlands", "Austria",
    "Switzerland", "Belgium", "Czechia", "Slovakia", "Hungary"
]


def prefill_database(api, db):
    """
    Автоматически инициализирует БД и собирает данные по 10 странам.
    Это необходимо для прохождения проверки на минимальное количество стран.
    """
    print("[Система] Инициализация базы данных и сбор начальных данных по 10 странам...")
    db.clear_aeroplanes()  # Очищаем таблицу самолетов перед свежим сканированием радара

    for country in REQUIRED_COUNTRIES:
        bounds = api._get_country_bounds(country)
        if not bounds:
            continue
        # Сохраняем страну и получаем её ID
        country_id = db.save_country(country, bounds)

        # Загружаем самолеты для этой страны
        raw_data = api.get_aeroplanes(country)
        if raw_data:
            planes = Aeroplane.cast_to_object_list(raw_data)
            for p in planes:
                db.save_aeroplane(p, country_id)

    print("[Система] База данных успешно заполнена начальными данными!\n")


def run_db_analytics(db):
    """Вызывает обязательные аналитические методы класса DBManager для демонстрации."""
    print("\n" + "=" * 20 + " ЗАПУСК АНАЛИТИКИ ИЗ ЗАДАНИЯ " + "=" * 20)

    # 1. Тест метода get_countries_and_aeroplanes_count()
    print("\n1. Количество самолетов по странам:")
    for row in db.get_countries_and_aeroplanes_count():
        print(f"   Страна: {row['name']} -> Самолетов в небе: {row['aeroplane_count']}")

    # 3. Тест метода get_avg_speed()
    avg_speed = db.get_avg_speed()
    print(f"\n2. Средняя скорость всех самолетов: {avg_speed:.2f} м/с")

    # 4. Тест метода get_aeroplanes_with_higher_speed()
    high_speed_planes = db.get_aeroplanes_with_higher_speed()
    print(f"3. Бортов со скоростью выше средней: {len(high_speed_planes)}")

    # 5. Тест метода get_aeroplanes_with_keyword()
    keyword = input("\nВведите ключевые символы позывного для поиска (например, 'ACA' или 'DLH'): ")
    kw_planes = db.get_aeroplanes_with_keyword(keyword)
    print(f"   Найдено самолетов с '{keyword}': {len(kw_planes)}")
    for p in kw_planes[:5]:  # Выведем первые 5 для примера
        print(f"   - ИКАО: {p['icao24']}, Позывной: {p['callsign']}, Скорость: {p['velocity']} м/с")

    print("=" * 69 + "\n")


def user_interaction():
    """Основная функция интерактивного взаимодействия с пользователем."""
    api = AircraftAPI()
    db = DBManager(DB_CONFIG)

    # Шаг 0: Выполняем жесткое требование по заполнению 10 стран
    prefill_database(api, db)

    print("--- Система мониторинга воздушного пространства ---")
    country = input("Введите название страны для поиска (на англ., например, 'Poland'): ")

    # Получаем координаты и сохраняем/обновляем страну в БД
    bounds = api._get_country_bounds(country)
    if not bounds:
        print("Страна не найдена.")
        db.close()
        return

    country_id = db.save_country(country, bounds)

    raw_data = api.get_aeroplanes(country)
    if not raw_data:
        print("Самолетов в небе этой страны сейчас нет.")
        db.close()
        return

    planes = Aeroplane.cast_to_object_list(raw_data)
    print(f"Найдено самолетов в реальном времени: {len(planes)}")

    try:
        n = int(input("Сколько самолетов вывести в Топ по высоте и обновить в БД? "))
    except ValueError:
        n = 5

    # Твоя крутая сортировка по высоте (использует __lt__ из класса Aeroplane)
    sorted_planes = sorted(planes, reverse=True)
    top_n = sorted_planes[:n]

    print(f"\nТоп-{n} самых высоколетящих бортов:")
    for p in top_n:
        print(p)
        # Вместо файла сохраняем самолет в базу данных PostgreSQL
        db.save_aeroplane(p, country_id)

    # Фильтрация по стране регистрации прямо из оперативной памяти (как у тебя и было)
    filter_country = input("\nВведите страну регистрации для фильтрации результатов: ")
    filtered = [p for p in planes if p.origin_country.lower() == filter_country.lower()]
    print(f"Найдено самолетов, зарегистрированных в {filter_country}: {len(filtered)}")
    for p in filtered[:10]:
        print(p)

    # Предлагаем запустить аналитические методы из задания курсовой
    ask_analytics = input("\nХотите запустить новые аналитические методы DBManager? (y/n): ")
    if ask_analytics.lower() in ['y', 'yes']:
        run_db_analytics(db)

    # Не забываем закрывать соединение с базой
    db.close()


if __name__ == "__main__":
    user_interaction()