from typing import Dict, List, Optional
from src.interfaces.repository import IFleetRepository
from src.interfaces.inventory import IInventoryItem
from src.interfaces.vehicle import IVehicle


class DuplicateInventoryNumberError(ValueError):
    """Исключение при попытке зарегистрировать дублирующий инвентарный номер."""
    pass


class InMemoryFleetRepository(IFleetRepository):
    """
    Репозиторий парка в оперативной памяти (In-Memory).
    Обеспечивает быстродействие и изолированность в тестах.
    """

    def __init__(self) -> None:
        self._vehicles: Dict[str, IVehicle] = {}
        self._items: Dict[str, IInventoryItem] = {}

    def add_vehicle(self, vehicle: IVehicle) -> None:
        inv = vehicle.inventory_number
        if self.exists_inventory_number(inv):
            raise DuplicateInventoryNumberError(
                f"Объект с инвентарным номером '{inv}' уже зарегистрирован в парке."
            )
        self._vehicles[inv] = vehicle

    def add_item(self, item: IInventoryItem) -> None:
        inv = item.inventory_number
        if self.exists_inventory_number(inv):
            raise DuplicateInventoryNumberError(
                f"Объект с инвентарным номером '{inv}' уже зарегистрирован на балансе."
            )
        self._items[inv] = item

    def get_vehicles(self) -> List[IVehicle]:
        return list(self._vehicles.values())

    def get_items(self) -> List[IInventoryItem]:
        return list(self._items.values())

    def get_all_inventory(self) -> List[IInventoryItem]:
        # Объединяем технику и вещи на балансе
        return list(self._vehicles.values()) + list(self._items.values())

    def exists_inventory_number(self, inventory_number: str) -> bool:
        return (inventory_number in self._vehicles) or (inventory_number in self._items)

    def find_by_inventory_number(self, inventory_number: str) -> Optional[IInventoryItem]:
        if inventory_number in self._vehicles:
            return self._vehicles[inventory_number]
        return self._items.get(inventory_number)

    def clear(self) -> None:
        """Очистить репозиторий (удобно для тестов)."""
        self._vehicles.clear()
        self._items.clear()
