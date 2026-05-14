import os
import glob
from comtrade_reader import ComtradeReader
from fault_detector import FaultDetector

# Путь к папке с COMTRADE-файлами
comtrade_folder = "3-20260506T185843Z-3-001"

# Создание экземпляра класса для работы с БД
db = ComtradeReader(db_path="comtrade.db")

# Поиск всех .cfg файлов в папке
cfg_files = glob.glob(os.path.join(comtrade_folder, "*.cfg"))

# Обработка каждого файла
for cfg_path in sorted(cfg_files):

    oscillogram_id = db.load_from_comtrade(cfg_path) # Загрузка данных из COMTRADE-файла в БД
    info = db.get_oscillogram_info(oscillogram_id) # Получение информации о загруженной осциллограмме

    if info:
        print("\nИнформация об осциллограмме:")
        print(f"ID: {info['oscillogram_id']}")
        print(f"Файл: {info['filename']}")
        print(f"Станция: {info['station_name']}")
        print(f"Версия: {info['version']}")
        print(f"Частота: {info['frequency']} Гц")
        print(f"Начало: {info['start_time']}")
        print(f"Конец: {info['end_time']}")
        print(f"Формат данных: {info['data_format']}")

    # Вывод информации о каналах
    channels = db.get_channels(oscillogram_id)
    print(f"\nКаналы ({len(channels)}):")
    for ch in channels:
        if ch['channel_type'] == 'A':
            print(f"  Канал {ch['channel_index']}: {ch['ch_id']} ({ch['phase']}) "
                  f"[{ch['channel_type']}], ед.изм: {ch['unit']}, "
                  f"a={ch['coeff_a']}, b={ch['coeff_b']}")
        else:
            print(f"  Канал {ch['channel_index']}: {ch['ch_id']} ({ch['phase']}) "
                  f"[{ch['channel_type']}], норм.состояние: {ch['normal_state']}")

    print(f"\nФайл обработан и добавлен в БД с ID: {oscillogram_id}")

    print("\nАнализ КЗ")
    detector = FaultDetector("comtrade.db", oscillogram_id)
    if detector.load_from_db():
        results = detector.analyze()
        detector.print_results(results)
