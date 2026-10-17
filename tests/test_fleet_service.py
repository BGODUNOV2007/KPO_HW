import unittest
from src.services.fleet_service import FleetService
from src.services.fleet_repository import InMemoryFleetRepository
from src.services.service_center import DefaultServiceCenter
from src.models.vehicle import KickScooter, Bicycle, ElectricBicycle
from src.models.items import Helmet, DockStation, ChargingCabinet
from src.models.employee import Employee


class TestFleetService(unittest.TestCase):
    """Тестирование основной бизнес-логики сервиса парка кикшеринга."""

    def setUp(self) -> None:
        self.repository = InMemoryFleetRepository()
        self.service_center = DefaultServiceCenter()
        self.service = FleetService(self.repository, self.service_center)

    def test_admit_vehicle_success_after_inspection(self) -> None:
        scooter = KickScooter("KS-100", "Xiaomi 4 Pro", simplicity_score=8, daily_energy_kwh=1.6, is_operational=True)
        result = self.service.admit_vehicle(scooter)

        self.assertTrue(result.success)
        self.assertIn("успешно зачислено в парк", result.message)
        self.assertEqual(len(self.service.get_all_vehicles()), 1)
        self.assertEqual(self.service.get_all_vehicles()[0], scooter)

    def test_admit_vehicle_rejected_by_service_center(self) -> None:
        broken_scooter = KickScooter("KS-101", "Xiaomi Broken", simplicity_score=8, daily_energy_kwh=1.6, is_operational=False)
        result = self.service.admit_vehicle(broken_scooter)

        self.assertFalse(result.success)
        self.assertIn("не пройден", result.message)
        # Главное требование ТЗ: техника НЕ попадает в парк!
        self.assertEqual(len(self.service.get_all_vehicles()), 0)

    def test_admit_duplicate_inventory_number_fails(self) -> None:
        scooter1 = KickScooter("KS-DUP", "Scooter 1", simplicity_score=7, daily_energy_kwh=1.0)
        scooter2 = KickScooter("KS-DUP", "Scooter 2", simplicity_score=7, daily_energy_kwh=1.0)

        res1 = self.service.admit_vehicle(scooter1)
        self.assertTrue(res1.success)

        res2 = self.service.admit_vehicle(scooter2)
        self.assertFalse(res2.success)
        self.assertIn("Ошибка сохранения в репозиторий", res2.message)
        self.assertEqual(len(self.service.get_all_vehicles()), 1)

    def test_admit_items_on_balance(self) -> None:
        helmet = Helmet("HLM-10", "Шлем город", size="M")
        dock = DockStation("DCK-10", "Станция Шаболовка", slots_count=12, daily_energy_kwh=4.0)

        self.service.admit_item(helmet)
        self.service.admit_item(dock)

        items = self.service.get_all_items()
        self.assertEqual(len(items), 2)
        self.assertIn(helmet, items)
        self.assertIn(dock, items)

    def test_admit_item_rejects_employee(self) -> None:
        """По ТЗ: сотрудники на баланс не ставятся!"""
        emp = Employee("EMP-99", "Дмитрий Ветров", "Диспетчер")
        with self.assertRaises(TypeError):
            self.service.admit_item(emp)  # type: ignore

    def test_total_daily_energy_consumption_calculation(self) -> None:
        scooter = KickScooter("KS-E1", "Scooter E", 8, daily_energy_kwh=1.5)
        bike = Bicycle("BK-E1", "Bike Regular", 9, gear_count=6)
        ebike = ElectricBicycle("EB-E1", "E-Bike", 5, daily_energy_kwh=2.2)
        helmet = Helmet("HLM-E1", "Helmet Sport")
        cabinet = ChargingCabinet("CHG-E1", "Big Cabinet", 20, daily_energy_kwh=15.3)

        self.service.admit_vehicle(scooter)
        self.service.admit_vehicle(bike)
        self.service.admit_vehicle(ebike)
        self.service.admit_item(helmet)
        self.service.admit_item(cabinet)

        expected_total = 1.5 + 2.2 + 15.3  # = 19.0 кВт·ч
        total = self.service.get_total_daily_energy_consumption()
        self.assertAlmostEqual(total, expected_total, places=2)

        breakdown = self.service.get_energy_breakdown()
        self.assertEqual(len(breakdown), 3)

    def test_get_novice_friendly_vehicles(self) -> None:
        v_easy1 = KickScooter("KS-1", "Easy Scooter", simplicity_score=6, daily_energy_kwh=1.0)
        v_easy2 = Bicycle("BK-1", "Simple Bike", simplicity_score=9, gear_count=3)
        v_hard = ElectricBicycle("EB-1", "Hard EBike", simplicity_score=4, daily_energy_kwh=2.0)

        self.service.admit_vehicle(v_easy1)
        self.service.admit_vehicle(v_easy2)
        self.service.admit_vehicle(v_hard)

        novices = self.service.get_novice_friendly_vehicles()
        self.assertEqual(len(novices), 2)
        self.assertIn(v_easy1, novices)
        self.assertIn(v_easy2, novices)
        self.assertNotIn(v_hard, novices)

    def test_get_all_inventory_report(self) -> None:
        scooter = KickScooter("KS-R1", "Scooter", 8, 1.2)
        helmet = Helmet("HLM-R1", "Helmet")

        self.service.admit_vehicle(scooter)
        self.service.admit_item(helmet)

        all_inv = self.service.get_all_inventory()
        self.assertEqual(len(all_inv), 2)
        inv_numbers = [item.inventory_number for item in all_inv]
        self.assertIn("KS-R1", inv_numbers)
        self.assertIn("HLM-R1", inv_numbers)

    def test_get_fleet_summary(self) -> None:
        scooter = KickScooter("KS-S1", "Scooter", 7, 2.0)
        dock = DockStation("DCK-S1", "Dock", 10, 3.0)

        self.service.admit_vehicle(scooter)
        self.service.admit_item(dock)

        summary = self.service.get_fleet_summary()
        self.assertEqual(summary.total_vehicles, 1)
        self.assertEqual(summary.total_items, 1)
        self.assertEqual(summary.total_inventory_units, 2)
        self.assertAlmostEqual(summary.total_daily_energy_kwh, 5.0, places=2)
        self.assertEqual(summary.novice_suitable_count, 1)

    def test_repository_find_and_clear(self) -> None:
        scooter = KickScooter("KS-F1", "Scooter Find", 7, 1.0)
        helmet = Helmet("HLM-F1", "Helmet Find")
        self.repository.add_vehicle(scooter)
        self.repository.add_item(helmet)

        self.assertEqual(self.repository.find_by_inventory_number("KS-F1"), scooter)
        self.assertEqual(self.repository.find_by_inventory_number("HLM-F1"), helmet)
        self.assertIsNone(self.repository.find_by_inventory_number("UNKNOWN"))

        self.repository.clear()
        self.assertEqual(len(self.repository.get_all_inventory()), 0)


if __name__ == "__main__":
    unittest.main()
