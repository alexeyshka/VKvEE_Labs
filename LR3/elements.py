from abc import ABC, abstractmethod

# Абстрактный класс, определяющий общий интерфейс для классов наследников
class Elements(ABC):

    @classmethod
    def create(cls, type, name, *args): # Реализация фабричного метода
        if type == 'inductance':
            return Inductance(name, *args)
        elif type == 'capacitance':
            return Capacitance(name, *args)
        elif type == 'resistance':
            return Resistance(name, *args)
        elif type == 'voltage_source':
            return VoltageSource(name, *args)

    @abstractmethod
    def get_J(self, phi=None, cur=None):
        pass
    @abstractmethod
    def get_G(self):
        pass

class Inductance(Elements):
    def __init__(self, name, nodes, branch, value, dt):
        self.name = name
        self.nodes = nodes
        self.branch = branch
        self.value = value
        self.dt = dt

    def get_G(self):
        return self.dt / (2 * self.value)
    def get_J(self, phi=None, cur=None):
        if phi is not None:
            phi1 = phi[self.nodes[1]] if self.nodes[1] <= phi.shape[0] - 1 else 0
            phi2 = phi[self.nodes[0]] if self.nodes[0] <= phi.shape[0] - 1 else 0
            voltage = phi1 - phi2
        else:
            voltage = 0
        current = cur[self.branch] if cur is not None else 0
        return current + voltage * self.dt / (2 * self.value)

class Capacitance(Elements):
    def __init__(self, name, nodes, branch, value, dt):
        self.name = name
        self.nodes = nodes
        self.branch = branch
        self.value = value
        self.dt = dt

    def get_G(self):
        return 2 * self.value / self.dt
    def get_J(self, phi=None, cur=None):
        if phi is not None:
            phi1 = phi[self.nodes[1]] if self.nodes[1] <= phi.shape[0] - 1 else 0
            phi2 = phi[self.nodes[0]] if self.nodes[0] <= phi.shape[0] - 1 else 0
            voltage = phi1 - phi2
        else:
            voltage = 0
        current = cur[self.branch] if cur is not None else 0
        return -current - 2 * self.value * voltage / self.dt

class Resistance(Elements):
    def __init__(self, name, nodes, branch, value, dt):
        self.name = name
        self.nodes = nodes
        self.branch = branch
        self.value = value
        self.dt = dt

    def get_G(self):
        return 1 / self.value
    def get_J(self, phi=None, cur=None):
        return 0

class VoltageSource(Elements):
    def __init__(self, name, nodes, branch, value, dt):
        self.name = name
        self.nodes = nodes
        self.branch = branch
        self.value = value
        self.dt = dt

    def get_G(self):
        return 1000000
    def get_J(self, phi=None, cur=None):
        return self.value/1000000