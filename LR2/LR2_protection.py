from LR2_equipment import Equipment, Bus, CircuitBreaker
from LR2_logger import logger
import time
import random

class Protection:
    def __init__(self, name, main_prob, backup_prob):
        self.__name = name
        self.__main_prob = float(main_prob)
        self.__backup_prob = float(backup_prob)
        self.__element = None
        self.__pickup_current = None
        self.__backup_current = None

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
    def get_backup_current(self):
        return self.__backup_current

    def connect(self, element):
        self.__element = element
        if element.get_voltage() == 330:
            self.__pickup_current = 40
            self.__backup_current = 30
        else:
            self.__pickup_current = 24
            self.__backup_current = 18

    def send_command(self):
        logger.info(f"Переключены выключатели:")
        qf_list = []
        for qf in self.__element.get_connections():
            CircuitBreaker.get_by_name(qf).switch()
            status = "ВКЛ" if CircuitBreaker.get_by_name(qf).get_is_on() else "ОТКЛ"
            qf_list.append(f"{qf}: {status}")
        logger.info(', '.join(map(str, qf_list)))
        self.__element.set_validity()

    def trip(self):
        if self.__element.get_current() < self.__pickup_current and random.random() < self.__main_prob:
            time.sleep(0.1)
            logger.info(f"Сработала основная защита {self.__name}")
            self.send_command()
        elif random.random() < self.__backup_prob:
            time.sleep(0.3)
            logger.info(f"Сработала резервная защита {self.__name}")
            self.send_command()
        else:
            time.sleep(0.3)
            logger.warning("Защита не сработала")


    def __repr__(self):
        return (f"{self.__class__.__name__} name={self.get_name()}, main_prob={self.get_main_prob()}, backup_prob={self.get_backup_prob()}, element={self.get_element()},"
                f"pickup_current={self.get_pickup_current()}, backup_current={self.get_backup_current()})")