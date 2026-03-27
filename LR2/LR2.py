import random
from LR2_json import load_json

# Создание списков с объектами класса оборудования, объектами класса КЗ
eq, sh_c, c_b, pr = load_json()

i = 0
while i < 10:
    print("test", i)
    faulted_equipment = eq[i]
    # Повреждение любого оборудования равновероятно
    num = random.randint(0, len(eq)-1)
    faulted_equipment = eq[num]
    faulted_equipment.set_validity()

    print("КЗ на ", faulted_equipment)
    # Тип КЗ определяется типом оборудования и вероятностью возникновения
    if faulted_equipment.__class__.__name__ == 'Transformer':
        sh_c_type = sh_c[3]
    else:
        weights = list(map(float, [x.get_probability() for x in sh_c[0:3]]))
        sh_c_type = random.choices(sh_c[0:3], weights)[0] # random.choices() всегда возвращает список
    sh_c_type.set_target(faulted_equipment)

    if sh_c_type.get_current() > pr[num].get_pickup_current():
        pr[num].trip()
        print("Сработала защита, переключены выключатели:")
        for qf in faulted_equipment.get_connections():
            print(qf)
    else:
        print(f"Защита не сработала, {sh_c_type.__class__.__name__} с током {sh_c_type.get_current()} < {pr[num].get_pickup_current()}")
    print(faulted_equipment)
    print()
    i += 1
