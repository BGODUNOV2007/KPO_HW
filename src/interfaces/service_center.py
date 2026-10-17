from abc import ABC, abstractmethod
from dataclasses import dataclass
from src.interfaces.vehicle import IVehicle


@dataclass(frozen=True)
class InspectionResult:
    """Результат техосмотра транспортного средства перед приёмкой в парк."""
    is_approved: bool
    reason: str


class IServiceCenter(ABC):
    """
    Интерфейс службы техосмотра (ServiceCenter).
    Решает, допускать ли новое транспортное средство к активной эксплуатации.
    Поддерживает Dependency Inversion Principle (DIP): сервис парка
    зависит от этого интерфейса, что позволяет подменять его заглушкой в тестах.
    """

    @abstractmethod
    def inspect(self, vehicle: IVehicle) -> InspectionResult:
        """
        Проводит техосмотр транспортного средства.
        :param vehicle: Проверяемое транспортное средство.
        :return: InspectionResult с вердиктом и причиной.
        """
        pass
