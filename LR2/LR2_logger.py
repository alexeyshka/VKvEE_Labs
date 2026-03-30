import logging

# Создание и настройка логгера
logger = logging.getLogger('SubstationLogger')
logger.setLevel(logging.DEBUG)

# Создание обработчика для записи логов в файл
file_handler = logging.FileHandler('SubstationLogger.log', mode='w')
file_handler.setLevel(logging.DEBUG)
#file_handler.flush()

# Создание обработчика для вывода логов в консоль
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.DEBUG)

# Создание форматтера для логов
formatter = logging.Formatter('%(asctime)s – %(levelname)s – %(message)s')
file_handler.setFormatter(formatter)
console_handler.setFormatter(formatter)

# Добавление обработчиков в логгер
logger.addHandler(file_handler)
logger.addHandler(console_handler)