import random
import time
from LR2_logger import logger
from LR2_json import load_json

# Создание списков с объектами класса оборудования, объектами класса КЗ
eq, sh_c, c_b, pr = load_json()

i = 0
while i < 10:
    logger.debug(f"{i + 1}-я итерация")

    # Повреждение оборудования любого типа равновероятно
    num = random.randint(0, len(eq)-1)
    faulted_equipment = eq[num]

    logger.info(f"КЗ на {faulted_equipment.get_name()}")

    # Установка типа КЗ. Тип КЗ определяется типом оборудования и вероятностью возникновения
    if faulted_equipment.__class__.__name__ == 'Transformer':
        sh_c_type = sh_c[3]
    else:
        weights = list(map(float, [x.get_probability() for x in sh_c[0:3]]))
        sh_c_type = random.choices(sh_c[0:3], weights)[0] # random.choices() всегда возвращает список

    # "Привязка" КЗ к оборудованию
    sh_c_type.set_target(faulted_equipment)
    logger.info(f"Тип КЗ: {sh_c_type.__class__.__name__}; Iкз = {sh_c_type.get_current()}")

    # Если не произошло самопогасания, работает защита
    if not faulted_equipment.get_is_valid(): pr[num].trip()

    time.sleep(1)
    i += 1
