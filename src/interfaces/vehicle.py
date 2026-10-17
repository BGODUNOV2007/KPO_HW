from abc import abstractmethod
from src.interfaces.inventory import IInventoryItem


class IVehicle(IInventoryItem):
    """
    Абстракция транспортного средства сервиса кикшеринга.
    Наследует IInventoryItem, так как любой транспорт ставится на баланс
    и имеет инвентарный номер.
    """

    @property
    @abstractmethod
    def simplicity_score(self) -> int:
        """
        Характеристика простоты управления для новичка (шкала от 1 до 10).
        """
        pass

    @abstractmethod
    def is_suitable_for_novice(self) -> bool:
        """
        Проверяет, подходит ли транспортное средство новичкам.
        Базовое правило: simplicity_score >= 6.
        """
        pass

    @property
    @abstractmethod
    def vehicle_type(self) -> str:
        """Тип транспортного средства (Самокат, Велосипед, Электровелосипед и т.д.)."""
        pass

    @property
    @abstractmethod
    def is_operational(self) -> bool:
        """Флаг технической исправности (проверяется техосмотром)."""
        pass
