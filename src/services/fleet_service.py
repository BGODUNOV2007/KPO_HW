from dataclasses import dataclass
from typing import List, Tuple, Optional
from src.interfaces.repository import IFleetRepository
from src.interfaces.service_center import IServiceCenter
from src.interfaces.inventory import IInventoryItem
from src.interfaces.vehicle import IVehicle
from src.interfaces.energy import IEnergyConsumer


@dataclass(frozen=True)
class AdmissionResult:
    """Результат попытки постановки транспортного средства в парк."""
    success: bool
    message: str
    vehicle: IVehicle


@dataclass(frozen=True)
class FleetSummary:
    """Сводный отчёт по состоянию парка «ВышКат»."""
    total_vehicles: int
    total_items: int
    total_inventory_units: int
    total_daily_energy_kwh: float
    novice_suitable_count: int


class FleetService:
    """
    Основной доменный сервис учёта парка «ВышКат».
    Реализует бизнес-логику управления флотом.
    В соответствии с DIP (Dependency Inversion Principle), зависит только
    от абстракций IFleetRepository и IServiceCenter, получаемых через DI.
    """

    def __init__(self, repository: IFleetRepository, service_center: IServiceCenter) -> None:
        self._repository = repository
        self._service_center = service_center

    def admit_vehicle(self, vehicle: IVehicle) -> AdmissionResult:
        """
        Приёмка транспортного средства в парк.
        Требование ТЗ: техника попадает в активный парк ТОЛЬКО после техосмотра!
        """
        inspection = self._service_center.inspect(vehicle)
        if not inspection.is_approved:
            return AdmissionResult(
                success=False,
                message=inspection.reason,
                vehicle=vehicle,
            )

        try:
            self._repository.add_vehicle(vehicle)
        except Exception as ex:
            return AdmissionResult(
                success=False,
                message=f"Ошибка сохранения в репозиторий: {ex}",
                vehicle=vehicle,
            )

        return AdmissionResult(
            success=True,
            message=f"{inspection.reason} Транспортное средство успешно зачислено в парк.",
            vehicle=vehicle,
        )

    def admit_item(self, item: IInventoryItem) -> None:
        """
        Постановка вещи/оборудования на баланс парка.
        Проверяет контракт IInventoryItem (сотрудники на баланс не ставятся!).
        """
        if not isinstance(item, IInventoryItem):
            raise TypeError(
                f"Объект типа {type(item).__name__} не реализует IInventoryItem "
                "и не может быть поставлен на баланс."
            )
        self._repository.add_item(item)

    def get_total_daily_energy_consumption(self) -> float:
        """
        Расчёт суммарного суточного энергопотребления парка (кВт·ч).
        Суммирует расход по всем потребителям ресурса (и техника, и инфраструктурные вещи).
        Объекты без интерфейса IEnergyConsumer (шлемы, обычные велосипеды) игнорируются.
        """
        total = 0.0
        for item in self._repository.get_all_inventory():
            if isinstance(item, IEnergyConsumer):
                total += item.daily_energy_kwh
        return round(total, 3)

    def get_energy_breakdown(self) -> List[Tuple[IInventoryItem, float]]:
        """
        Детальный отчёт по потреблению энергии каждым потребителем.
        """
        result: List[Tuple[IInventoryItem, float]] = []
        for item in self._repository.get_all_inventory():
            if isinstance(item, IEnergyConsumer):
                result.append((item, item.daily_energy_kwh))
        return result

    def get_novice_friendly_vehicles(self) -> List[IVehicle]:
        """
        Список прокатной техники, подходящей для новичков.
        Правило: vehicle.is_suitable_for_novice() (базово simplicity_score >= 6).
        """
        return [v for v in self._repository.get_vehicles() if v.is_suitable_for_novice()]

    def get_all_vehicles(self) -> List[IVehicle]:
        """Список всей техники в активном парке."""
        return self._repository.get_vehicles()

    def get_all_items(self) -> List[IInventoryItem]:
        """Список всех вещей/оборудования на балансе."""
        return self._repository.get_items()

    def get_all_inventory(self) -> List[IInventoryItem]:
        """Список абсолютно всего имущества парка с инвентарными номерами."""
        return self._repository.get_all_inventory()

    def get_fleet_summary(self) -> FleetSummary:
        """Формирует сводный отчёт по парку."""
        vehicles = self.get_all_vehicles()
        items = self.get_all_items()
        novice = self.get_novice_friendly_vehicles()
        energy = self.get_total_daily_energy_consumption()

        return FleetSummary(
            total_vehicles=len(vehicles),
            total_items=len(items),
            total_inventory_units=len(vehicles) + len(items),
            total_daily_energy_kwh=energy,
            novice_suitable_count=len(novice),
        )
