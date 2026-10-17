from abc import ABC, abstractmethod
from typing import List, Optional
from src.interfaces.inventory import IInventoryItem
from src.interfaces.vehicle import IVehicle


class IFleetRepository(ABC):
    """
    Интерфейс хранилища парка (FleetRepository).
    Инкапсулирует хранение и поиск инвентаря и техники на балансе.
    """

    @abstractmethod
    def add_vehicle(self, vehicle: IVehicle) -> None:
        """Сохранить транспортное средство в активном парке."""
        pass

    @abstractmethod
    def add_item(self, item: IInventoryItem) -> None:
        """Поставить вещь на баланс парка."""
        pass

    @abstractmethod
    def get_vehicles(self) -> List[IVehicle]:
        """Получить список всех транспортных средств в парке."""
        pass

    @abstractmethod
    def get_items(self) -> List[IInventoryItem]:
        """Получить список всех вещей/оборудования на балансе."""
        pass

    @abstractmethod
    def get_all_inventory(self) -> List[IInventoryItem]:
        """Получить полный список всех объектов (техника + вещи) на балансе."""
        pass

    @abstractmethod
    def exists_inventory_number(self, inventory_number: str) -> bool:
        """Проверить, зарегистрирован ли уже объект с данным инвентарным номером."""
        pass

    @abstractmethod
    def find_by_inventory_number(self, inventory_number: str) -> Optional[IInventoryItem]:
        """Найти объект по инвентарному номеру."""
        pass
