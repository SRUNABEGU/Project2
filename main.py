from src.abc_api import AircraftAPI
from src.aeroplane import Aeroplane
from src.savers import JSONSaver


def user_interaction():
    api = AircraftAPI()
    saver = JSONSaver()

    print("--- Система мониторинга воздушного пространства ---")
    country = input("Введите название страны (на англ., например, 'Poland'): ")

    raw_data = api.get_aeroplanes(country)
    if not raw_data:
        print("Самолетов в небе этой страны сейчас нет.")
        return

    planes = Aeroplane.cast_to_object_list(raw_data)
    print(f"Найдено самолетов: {len(planes)}")

    try:
        n = int(input("Сколько самолетов вывести в Топ по высоте? "))
    except ValueError:
        n = 5

    sorted_planes = sorted(planes, reverse=True)
    top_n = sorted_planes[:n]

    print(f"\nТоп-{n} самых высоколетящих бортов:")
    for p in top_n:
        print(p)
        saver.add_aeroplane(p)

    filter_country = input("\nВведите страну регистрации для фильтрации: ")
    filtered = [p for p in planes if p.origin_country.lower() == filter_country.lower()]
    print(f"Найдено самолетов из {filter_country}: {len(filtered)}")
    for p in filtered[:10]:
        print(p)


if __name__ == "__main__":
    user_interaction()