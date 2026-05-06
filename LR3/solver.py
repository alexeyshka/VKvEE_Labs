import numpy as np
from elements import *

class Solver:
    def __init__(self, g_n, g_b, j_b, a, elem_arr):
        self.g_n = np.delete(np.delete(g_n, g_n.shape[0] - 1, 1), g_n.shape[0] - 1, 0)
        self.g_b = g_b
        self.j_b = j_b
        self.a = np.delete(a, a.shape[0] - 1, 0)
        self.elem_arr = elem_arr

    def solve(self, dt, t_end, name):
        t_step = 0
        phi = np.zeros(self.g_n.shape[0]) # Вектор мгновенных потенциалов узлов
        i = np.zeros(self.j_b.shape) # Вектор мгновенных токов в ветвях
        u_t = [] # Массив напряжения от времени на необходимом элементе
        i_t = []
        t = []
        g_b_n = self.g_b @ self.a.T
        while t_step <= t_end:
            for element in self.elem_arr: # Перерасчет источников тока для реактивных элементов
                self.j_b[element.branch] = element.get_J(phi, i)
            j_n = -self.a @ self.j_b # Вектор-столбец "узловых" токов (отрицательный знак для истории)
            phi = np.linalg.inv(self.g_n) @ j_n # Расчет потенциалов по МУП
            i = g_b_n @ phi + self.j_b # Расчет токов по второму закону Кирхгофа
            t.append(t_step)
            for element in self.elem_arr:
                if element.name == name:
                    phi1 = phi[element.nodes[1]] if element.nodes[1] <= phi.shape[0] - 1 else 0
                    phi2 = phi[element.nodes[0]] if element.nodes[0] <= phi.shape[0] - 1 else 0
                    u_t.append(phi1 - phi2)
                    i_t.append(i[element.branch])
            t_step += dt
        return u_t, i_t, t