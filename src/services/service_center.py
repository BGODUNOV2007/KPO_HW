from src.interfaces.service_center import IServiceCenter, InspectionResult
from src.interfaces.vehicle import IVehicle
from src.interfaces.energy import IEnergyConsumer


class DefaultServiceCenter(IServiceCenter):
    """
    Реализация сервиса технического осмотра сервиса «ВышКат».
    Проверяет физическое состояние и параметры безопасности техники перед добавлением в парк.
    """

    def inspect(self, vehicle: IVehicle) -> InspectionResult:
        """
        Проводит техосмотр техники.
        Если техника неисправна или параметры некорректны — отклоняет приёмку.
        """
        if not vehicle.is_operational:
            return InspectionResult(
                is_approved=False,
                reason=f"Техосмотр не пройден: транспортное средство '{vehicle.name}' "
                       f"({vehicle.inventory_number}) имеет технические неисправности."
            )

        # Проверка энергопотребителей на аномальный расход
        if isinstance(vehicle, IEnergyConsumer):
            if vehicle.daily_energy_kwh > 50.0:
                return InspectionResult(
                    is_approved=False,
                    reason=f"Техосмотр не пройден: аномально высокий расход энергии "
                           f"({vehicle.daily_energy_kwh} кВт·ч/сут) указывает на утечку или КЗ."
                )

        return InspectionResult(
            is_approved=True,
            reason=f"Техосмотр успешно пройден: транспортное средство '{vehicle.name}' "
                   f"допущено к активной эксплуатации."
        )
