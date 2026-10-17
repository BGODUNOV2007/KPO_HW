import unittest
from unittest.mock import MagicMock

from src.container.di_container import DIContainer, ServiceNotFoundError, create_app_container
from src.interfaces.service_center import IServiceCenter, InspectionResult
from src.interfaces.repository import IFleetRepository
from src.interfaces.vehicle import IVehicle
from src.services.fleet_repository import InMemoryFleetRepository
from src.services.fleet_service import FleetService
from src.models.vehicle import KickScooter


# --- Тестовые заглушки (Stubs) для техосмотра ---

class AlwaysRejectServiceCenterStub(IServiceCenter):
    """Тестовая заглушка (Stub), которая всегда отклоняет техосмотр."""

    def __init__(self, rejection_message: str = "Тестовый отказ: стенд неисправен") -> None:
        self.rejection_message = rejection_message

    def inspect(self, vehicle: IVehicle) -> InspectionResult:
        return InspectionResult(is_approved=False, reason=self.rejection_message)


class AlwaysApproveServiceCenterStub(IServiceCenter):
    """Тестовая заглушка (Stub), которая всегда одобряет техосмотр."""

    def inspect(self, vehicle: IVehicle) -> InspectionResult:
        return InspectionResult(is_approved=True, reason="Тестовое безусловное одобрение.")


# --- Тесты DI-контейнера и подмены зависимостей ---

class TestDIContainerAndSubstitution(unittest.TestCase):
    """
    Тестирование DI-контейнера и подмены зависимости техосмотра (Критерий 3 ТЗ).
    Демонстрирует применение принципа инверсии зависимостей (DIP).
    """

    def test_container_singleton_lifecycle(self) -> None:
        container = DIContainer()
        container.register_singleton(IFleetRepository, InMemoryFleetRepository)

        repo1 = container.resolve(IFleetRepository)
        repo2 = container.resolve(IFleetRepository)

        self.assertIs(repo1, repo2)

    def test_container_transient_lifecycle(self) -> None:
        container = DIContainer()
        container.register_transient(IFleetRepository, InMemoryFleetRepository)

        repo1 = container.resolve(IFleetRepository)
        repo2 = container.resolve(IFleetRepository)

        self.assertIsNot(repo1, repo2)

    def test_container_unregistered_service_raises_error(self) -> None:
        container = DIContainer()
        with self.assertRaises(ServiceNotFoundError):
            container.resolve(IServiceCenter)

    def test_di_substitution_with_reject_stub(self) -> None:
        """
        Тест фиксирует подмену IServiceCenter через DI на AlwaysRejectServiceCenterStub.
        Проверяет, что исправное ТС будет отклонено, так как FleetService использует подменённый сервис.
        """
        container = DIContainer()
        container.register_singleton(IFleetRepository, InMemoryFleetRepository)
        reject_stub = AlwaysRejectServiceCenterStub("Служба техосмотра на карантине")
        container.register_instance(IServiceCenter, reject_stub)
        container.register_singleton(FleetService)

        fleet_service = container.resolve(FleetService)
        healthy_scooter = KickScooter("KS-TEST-01", "Healthy Scooter", 8, 1.2, is_operational=True)

        admission = fleet_service.admit_vehicle(healthy_scooter)

        self.assertFalse(admission.success)
        self.assertIn("Служба техосмотра на карантине", admission.message)
        self.assertEqual(len(fleet_service.get_all_vehicles()), 0)

    def test_di_substitution_with_approve_stub(self) -> None:
        """
        Тест фиксирует подмену IServiceCenter через DI на AlwaysApproveServiceCenterStub.
        Проверяет, что ТС принимается при безусловном одобрении заглушки.
        """
        container = DIContainer()
        container.register_singleton(IFleetRepository, InMemoryFleetRepository)
        approve_stub = AlwaysApproveServiceCenterStub()
        container.register_instance(IServiceCenter, approve_stub)
        container.register_singleton(FleetService)

        fleet_service = container.resolve(FleetService)
        scooter = KickScooter("KS-TEST-02", "Scooter", 6, 1.0, is_operational=True)

        admission = fleet_service.admit_vehicle(scooter)
        self.assertTrue(admission.success)
        self.assertIn("Тестовое безусловное одобрение", admission.message)
        self.assertEqual(len(fleet_service.get_all_vehicles()), 1)

    def test_di_substitution_with_mock_behavior_verification(self) -> None:
        """
        Тест фиксирует поведение через MagicMock:
        проверяет, что FleetService вызывает inspect() ровно 1 раз с переданным объектом.
        """
        container = DIContainer()
        container.register_singleton(IFleetRepository, InMemoryFleetRepository)

        mock_service_center = MagicMock(spec=IServiceCenter)
        mock_service_center.inspect.return_value = InspectionResult(
            is_approved=True, reason="Mock подтвердил безопасность."
        )

        container.register_instance(IServiceCenter, mock_service_center)
        container.register_singleton(FleetService)

        fleet_service = container.resolve(FleetService)
        test_scooter = KickScooter("KS-MOCK", "Mock Scooter", 7, 1.5)

        admission = fleet_service.admit_vehicle(test_scooter)

        mock_service_center.inspect.assert_called_once_with(test_scooter)
        self.assertTrue(admission.success)
        self.assertIn("Mock подтвердил безопасность", admission.message)

    def test_default_app_container_factory(self) -> None:
        """Проверяет фабрику приложения create_app_container()."""
        container = create_app_container()
        fleet_service = container.resolve(FleetService)
        self.assertIsInstance(fleet_service, FleetService)


if __name__ == "__main__":
    unittest.main()
