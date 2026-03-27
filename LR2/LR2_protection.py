from LR2_equipment import Equipment, Bus, CircuitBreaker

class Protection:
    def __init__(self, name, main_prob, backup_prob, element=None, pickup_current=None):
        self.__name = name
        self.__main_prob = main_prob
        self.__backup_prob = backup_prob
        self.__element = element
        self.__pickup_current = pickup_current

    def get_name(self):
        return self.__name
    def get_main_prob(self):
        return self.__main_prob
    def get_backup_prob(self):
        return self.__backup_prob
    def get_element(self):
        return self.__element
    def get_pickup_current(self):
        return self.__pickup_current

    def connect(self, element):
        self.__element = element
        self.__pickup_current = 800 if element.get_voltage() == 330 else 400

    def trip(self):
        for qf in self.__element.get_connections():
            CircuitBreaker.get_by_name(qf).switch()
            self.__element.set_validity()
        return

    def __repr__(self):
        return f"{self.__class__.__name__} name={self.get_name()}, main_prob={self.get_main_prob()}, backup_prob={self.get_backup_prob()}, element={self.get_element()})"