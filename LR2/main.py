import random
import time
from logger import logger
from json_reader import load_json
from equipment import CircuitBreaker

# Создание списков с объектами класса оборудования, класса КЗ, класса выключателей и класса защиты
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
    qf_list = []

    # Если не произошло самопогасания
    if not faulted_equipment.get_is_valid():
        logger.info(f"Тип КЗ: {sh_c_type.__class__.__name__}; Iкз = {sh_c_type.get_current():.3f} кА")
        # Срабатывание соответствующей защиты
        pr[num].trip()
        # Если защита не сработала
        if not faulted_equipment.get_is_valid():
            logger.warning(f"Оборудование {faulted_equipment.get_name()} повреждено")
            faulted_equipment.set_validity() # Возврат к рабочему состоянию для следующей итерации
        else:
            # Иначе возврат в исходное состояние выключателей элемента
            for qf in faulted_equipment.get_connections():
                CircuitBreaker.get_by_name(qf).switch()

    time.sleep(1)
    i += 1
