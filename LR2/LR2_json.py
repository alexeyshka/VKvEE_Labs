from LR2_equipment import Equipment, Transformer, CircuitBreaker, Line, Bus
from LR2_faults import OnePhaseFault, TwoPhaseFault, ThreePhaseFault, TurnToTurnFault
from LR2_protection import Protection
import json

def load_json():
    with open('test.json', 'r') as file:
        data = json.load(file) # Создает словарь с данными из файла

    equipment_list = []
    circuitbreakers_list = []
    faults_list = []
    protection_list = []

    # Итерация по всем элементам словаря 'Equipment'. При его отсутствии возвращает пустой словарь
    for class_type, class_items in data.items():
        if class_type == 'Equipment':
            for object_type, object_values in class_items.items():
                for object_data in object_values.items():
                    # globals() возвращает словарь всех глобальных имен
                    # передача словаря через оператор ** присваивает значения соответствующи именованным аргументам
                    obj = globals()[object_type](**object_data[1])
                    equipment_list.append(obj)
        elif class_type == 'Faults':
            for object_type, object_values in class_items.items():
                obj = globals()[object_type](**object_values)
                faults_list.append(obj)
        else:
            for object_type, object_values in class_items.items():
                obj = globals()[class_type](**object_values)
                if class_type == 'CircuitBreaker':
                    circuitbreakers_list.append(obj)
                else:
                    # Если объект класса Protection к нему добавляется соответствующий элемент Equipment
                    obj.connect(Equipment.get_by_name(object_type))
                    protection_list.append(obj)

    return equipment_list, faults_list, circuitbreakers_list, protection_list
