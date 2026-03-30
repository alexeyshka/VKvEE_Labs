from LR2_logger import logger
import random

class Faults:
    def __init__(self, probability, self_extinct, target=None):
        self.__probability = float(probability)
        self.__self_extinct = float(self_extinct)
        self.__target = target
        self.base_current = None

    def get_probability(self):
        return self.__probability
    def get_self_extinct(self):
        return self.__self_extinct
    def get_target(self):
        return self.__target

    # При определении поврежденного объекта инициализируется атрибут base_current,
    # определяющий величину тока КЗ в зависимости от класса напряжения оборудования
    def set_target(self, target):
        self.__target = target
        self.base_current = 50 if target.get_voltage() == 330 else 30
        self._set_current() # Метод наследуемых классов, возвращающий посчитанное значение тока
        if random.random() > self.__self_extinct:
            self.__target.set_current(self.get_current())
            self.__target.set_validity()
        else:
            logger.info("КЗ было самоустранено")

    # Геттер и сеттер атрибута current наследуемых классов, в которых они переопределены
    def get_current(self):
        pass
    def _set_current(self):
        pass

    # Метод для вывода всех атрибутов класса
    def __repr__(self):
        return f"{self.__class__.__name__}(probability={self.get_probability()}, self_extinct={self.get_self_extinct()}, current={self.get_current()}, target={self.get_target()})"

class OnePhaseFault(Faults):
    def __init__(self, probability, self_extinct, target=None):
        super().__init__(probability, self_extinct, target)
        self.__current = 0

    def get_current(self):
        return self.__current
    def _set_current(self):
        self.__current = random.uniform(self.base_current * 0.5, self.base_current * 0.75)

class TwoPhaseFault(Faults):
    def __init__(self, probability, self_extinct, target=None):
        super().__init__(probability, self_extinct, target)
        self.__current = 0

    def get_current(self):
        return self.__current
    def _set_current(self):
        self.__current = random.uniform(self.base_current * 0.75, self.base_current * 1)

class ThreePhaseFault(Faults):
    def __init__(self, probability, self_extinct, target=None):
        super().__init__(probability, self_extinct, target)
        self.__current = 0

    def get_current(self):
        return self.__current
    def _set_current(self):
        self.__current = random.uniform(self.base_current * 0.9, self.base_current * 1.2)

class TurnToTurnFault(Faults):
    def __init__(self, probability, self_extinct, target=None):
        super().__init__(probability, self_extinct, target)
        self.__current = 0

    def get_current(self):
        return self.__current
    def _set_current(self):
        self.__current = random.uniform(self.base_current * 0.4, self.base_current * 0.8)