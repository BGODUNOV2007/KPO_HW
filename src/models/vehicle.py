from abc import ABC
from src.interfaces.vehicle import IVehicle
from src.interfaces.energy import IEnergyConsumer


class BaseVehicle(IVehicle, ABC):
    """
    Базовый класс транспортного средства.
    Реализует общий контракт IVehicle и IInventoryItem.
    """

    def __init__(
        self,
        inventory_number: str,
        name: str,
        simplicity_score: int,
        is_operational: bool = True,
    ) -> None:
        if not inventory_number or not inventory_number.strip():
            raise ValueError("Инвентарный номер не может быть пустым.")
        if not name or not name.strip():
            raise ValueError("Наименование не может быть пустым.")
        if not (1 <= simplicity_score <= 10):
            raise ValueError(
                f"Характеристика 'простота для новичка' должна быть в диапазоне от 1 до 10 (получено {simplicity_score})."
            )

        self._inventory_number = inventory_number.strip()
        self._name = name.strip()
        self._simplicity_score = simplicity_score
        self._is_operational = is_operational

    @property
    def inventory_number(self) -> str:
        return self._inventory_number

    @property
    def name(self) -> str:
        return self._name

    @property
    def item_category(self) -> str:
        return "Транспорт"

    @property
    def simplicity_score(self) -> int:
        return self._simplicity_score

    @property
    def is_operational(self) -> bool:
        return self._is_operational

    def is_suitable_for_novice(self) -> bool:
        """По ТЗ: при значении >= 6 устройство можно выдавать новичкам."""
        return self._simplicity_score >= 6

    def __repr__(self) -> str:
        return (
            f"<{self.vehicle_type} #{self.inventory_number}: '{self.name}', "
            f"простота={self.simplicity_score}/10, исправен={self.is_operational}>"
        )


class KickScooter(BaseVehicle, IEnergyConsumer):
    """
    Электросамокат сервиса «ВышКат».
    Является транспортным средством и потребителем электроэнергии.
    """

    def __init__(
        self,
        inventory_number: str,
        name: str,
        simplicity_score: int,
        daily_energy_kwh: float,
        is_operational: bool = True,
    ) -> None:
        super().__init__(inventory_number, name, simplicity_score, is_operational)
        if daily_energy_kwh < 0:
            raise ValueError("Суточный расход энергии не может быть отрицательным.")
        self._daily_energy_kwh = float(daily_energy_kwh)

    @property
    def vehicle_type(self) -> str:
        return "Электросамокат"

    @property
    def daily_energy_kwh(self) -> float:
        return self._daily_energy_kwh


class Bicycle(BaseVehicle):
    """
    Механический велосипед.
    Является транспортом, но НЕ является потребителем энергии (ISP в действии).
    """

    def __init__(
        self,
        inventory_number: str,
        name: str,
        simplicity_score: int,
        gear_count: int = 7,
        is_operational: bool = True,
    ) -> None:
        super().__init__(inventory_number, name, simplicity_score, is_operational)
        if gear_count < 1:
            raise ValueError("Количество передач должно быть не менее 1.")
        self.gear_count = gear_count

    @property
    def vehicle_type(self) -> str:
        return "Механический велосипед"


class ElectricBicycle(BaseVehicle, IEnergyConsumer):
    """
    Электровелосипед.
    Сочетает велосипедную механику и электротягу, потребляет ресурс.
    """

    def __init__(
        self,
        inventory_number: str,
        name: str,
        simplicity_score: int,
        daily_energy_kwh: float,
        motor_power_w: int = 250,
        is_operational: bool = True,
    ) -> None:
        super().__init__(inventory_number, name, simplicity_score, is_operational)
        if daily_energy_kwh < 0:
            raise ValueError("Суточный расход энергии не может быть отрицательным.")
        if motor_power_w <= 0:
            raise ValueError("Мощность мотора должна быть положительной.")
        self._daily_energy_kwh = float(daily_energy_kwh)
        self.motor_power_w = motor_power_w

    @property
    def vehicle_type(self) -> str:
        return "Электровелосипед"

    @property
    def daily_energy_kwh(self) -> float:
        return self._daily_energy_kwh
