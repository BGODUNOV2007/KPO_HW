from abc import ABC, abstractmethod


class IEnergyConsumer(ABC):
    """
    Абстракция для объектов, потребляющих электроэнергию (ресурс).
    Соблюдает Interface Segregation Principle (ISP): устройства без энергопотребления
    (например, механические велосипеды или шлемы) не обязаны реализовывать этот интерфейс.
    """

    @property
    @abstractmethod
    def daily_energy_kwh(self) -> float:
        """Суточный расход электроэнергии в кВт·ч."""
        pass
