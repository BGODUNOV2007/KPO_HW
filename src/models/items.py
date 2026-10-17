from abc import ABC
from src.interfaces.inventory import IInventoryItem
from src.interfaces.energy import IEnergyConsumer


class BaseItem(IInventoryItem, ABC):
    """
    Базовый класс инвентарной вещи/оборудования на балансе парка.
    """

    def __init__(self, inventory_number: str, name: str, category: str = "Имущество") -> None:
        if not inventory_number or not inventory_number.strip():
            raise ValueError("Инвентарный номер вещи не может быть пустым.")
        if not name or not name.strip():
            raise ValueError("Наименование вещи не может быть пустым.")

        self._inventory_number = inventory_number.strip()
        self._name = name.strip()
        self._category = category

    @property
    def inventory_number(self) -> str:
        return self._inventory_number

    @property
    def name(self) -> str:
        return self._name

    @property
    def item_category(self) -> str:
        return self._category

    def __repr__(self) -> str:
        return f"<{self._category} #{self.inventory_number}: '{self.name}'>"


class Helmet(BaseItem):
    """
    Защитный шлем для пользователей сервиса «ВышКат».
    Ставится на баланс (инвентаризируется), но НЕ потребляет энергию.
    """

    def __init__(self, inventory_number: str, name: str, size: str = "M") -> None:
        super().__init__(inventory_number, name, category="Экипировка")
        self.size = size


class DockStation(BaseItem, IEnergyConsumer):
    """
    Док-станция (парковочный модуль с замками и телеметрией).
    Потребляет электроэнергию на поддержание связности и замковых механизмов.
    """

    def __init__(
        self,
        inventory_number: str,
        name: str,
        slots_count: int,
        daily_energy_kwh: float = 3.0,
    ) -> None:
        super().__init__(inventory_number, name, category="Инфраструктура")
        if slots_count <= 0:
            raise ValueError("Количество слотов док-станции должно быть больше 0.")
        if daily_energy_kwh < 0:
            raise ValueError("Расход энергии не может быть отрицательным.")
        self.slots_count = slots_count
        self._daily_energy_kwh = float(daily_energy_kwh)

    @property
    def daily_energy_kwh(self) -> float:
        return self._daily_energy_kwh


class ChargingCabinet(BaseItem, IEnergyConsumer):
    """
    Зарядный шкаф для сменных аккумуляторов самокатов.
    Потребляет значительное количество электроэнергии в сутки.
    """

    def __init__(
        self,
        inventory_number: str,
        name: str,
        battery_slots: int,
        daily_energy_kwh: float = 15.0,
    ) -> None:
        super().__init__(inventory_number, name, category="Зарядное оборудование")
        if battery_slots <= 0:
            raise ValueError("Количество ячеек для аккумуляторов должно быть больше 0.")
        if daily_energy_kwh < 0:
            raise ValueError("Расход энергии не может быть отрицательным.")
        self.battery_slots = battery_slots
        self._daily_energy_kwh = float(daily_energy_kwh)

    @property
    def daily_energy_kwh(self) -> float:
        return self._daily_energy_kwh
