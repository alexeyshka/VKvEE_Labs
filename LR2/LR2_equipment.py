class Equipment:
    __registry = {}
    def __init__(self, name, connections=None, voltage=None, is_valid=True, current=None):
        self.__connections = [] if connections is None else connections
        self.__name = name
        self.__voltage = voltage
        self.__is_valid = is_valid
        self.__current = current
        Equipment.__registry[name] = self

    @classmethod
    def get_by_name(csl, name):
        if name in csl.__registry:
            return csl.__registry[name]

    def get_name(self):
        return self.__name
    def get_voltage(self):
        return self.__voltage
    def get_is_valid(self):
        return self.__is_valid
    def get_connections(self):
        return self.__connections
    def get_current(self):
        return self.__current

    def set_validity(self):
        self.__is_valid = not self.__is_valid
    def set_current(self, current):
        self.__current = current

    def __repr__(self):
        return (f"{self.__class__.__name__}(name={self.get_name()}, voltage={self.get_voltage()},"
                f"connections={self.get_connections()}, is_valid={self.get_is_valid()}, current={self.get_current()})")

class Transformer(Equipment):
    pass

class Line(Equipment):
    pass

class Bus(Equipment):
    pass

class CircuitBreaker():
    # Словарь с элементами имя-объект
    __registry = {}
    def __init__(self, name, is_on=True):
        self.__name = name
        self.__is_on = is_on
        CircuitBreaker.__registry[name] = self

    # Поскольку словарь registry – атрибут класса, необходим декоратор метода класса
    @classmethod
    def get_by_name(csl, name):
        if name in csl.__registry:
            return csl.__registry[name]

    def get_name(self):
        return self.__name
    def get_is_on(self):
        return self.__is_on

    def switch(self):
        self.__is_on = not self.__is_on

    def __repr__(self):
        return f"{self.__class__.__name__}(name={self.get_name()}, is_on={self.get_is_on()})"
