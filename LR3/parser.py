import json
import numpy as np
from elements import *

# Добавляет элемент в матрицу проводимостей по методу поэлементного вклада
def g_add(matrix, index_list, value): # Принимает изменяемую матрицу, номера начального и конечного узлов элемента, значение его сопротивления
    i = index_list[0]
    j = index_list[1]
    matrix[i, i] += value
    matrix[j, j] += value
    matrix[i, j] -= value
    matrix[j, i] -= value

 # Возвращает количество узлов, количество ветвей и шаг расчета
def scheme_data(filename):
    nodes = set() # Множество узлов (для исключения повторяющихся)
    branches = set() # Множество ветвей
    time_step = 0

    with open(filename, 'r') as file:
        data = json.load(file) # Создает словарь с данными из файла

    for class_type, class_items in data.items():
        if class_type == 'elements':
            for name, parameters in class_items.items(): # Цикл по элементам схемы
                branches.add(parameters['branch'])
                for i in (0, 1):
                    if parameters['nodes'][i] not in nodes:
                        nodes.add(parameters['nodes'][i])
        elif class_type == 'solver':
            time_step = class_items["time_step"]
            elem_name = class_items["element"]

    return len(nodes), len(branches), time_step, elem_name


def load_json(filename, n, b, t):

    g_n = np.zeros((n, n)) # Нулевая квадратная матрица узловых проводимостей
    g_b = np.zeros((b, b)) # Нулевая диагональная матрица проводимостей ветвей
    j_b = np.zeros(b) # Нулевой вектор-столбец источников токов в ветвях
    a = np.zeros((n, b)) # Нулевая матрица соединений
    elem_arr = [] # Массив реактивных элементов

    with open(filename, 'r') as file:
        data = json.load(file) # Словарь с данными из файла

    for class_type, class_items in data.items():
        if class_type == 'elements':
            for name, parameters in class_items.items():
                elem_type = parameters['type']
                elem_val = parameters['value']
                elem_branch = parameters['branch']
                elem_nodes = parameters['nodes']
                # Заполнение матрицы соединений
                a[elem_nodes[0], elem_branch] = -1 # Ветвь направлена от узла
                a[elem_nodes[1], elem_branch] = 1 # Ветвь направлена к узлу
                if name == 'current_source':
                    # У источников тока проводимость нулевая; достаточно заполнения соответствующих векторов
                    j_b[elem_branch] = elem_val
                else:
                    # Для не источников тока, необходим расчет проводимости
                    elem = Elements.create(elem_type, name, elem_nodes, elem_branch, elem_val, t)
                    j_b[elem_branch] = elem.get_J()
                    g_add(g_n, elem_nodes, elem.get_G())
                    g_b[elem_branch, elem_branch] = elem.get_G()
                    elem_arr.append(elem)

    return g_n, g_b, j_b, a, elem_arr
