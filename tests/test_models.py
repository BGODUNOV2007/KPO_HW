import unittest
from src.interfaces.inventory import IInventoryItem
from src.interfaces.energy import IEnergyConsumer
from src.interfaces.vehicle import IVehicle
from src.models.vehicle import BaseVehicle, KickScooter, Bicycle, ElectricBicycle
from src.models.items import Helmet, DockStation, ChargingCabinet, BaseItem
from src.models.employee import Employee


class TestVehicleModels(unittest.TestCase):
    """Тестирование доменных моделей транспорта и правила 'для новичков'."""

    def test_kick_scooter_creation_and_interfaces(self) -> None:
        scooter = KickScooter(
            inventory_number="KS-01",
            name="Ninebot Max",
            simplicity_score=8,
            daily_energy_kwh=1.5,
            is_operational=True,
        )
        self.assertIsInstance(scooter, IVehicle)
        self.assertIsInstance(scooter, IInventoryItem)
        self.assertIsInstance(scooter, IEnergyConsumer)
        self.assertEqual(scooter.inventory_number, "KS-01")
        self.assertEqual(scooter.name, "Ninebot Max")
        self.assertEqual(scooter.simplicity_score, 8)
        self.assertEqual(scooter.daily_energy_kwh, 1.5)
        self.assertEqual(scooter.vehicle_type, "Электросамокат")
        self.assertEqual(scooter.item_category, "Транспорт")
        self.assertTrue(scooter.is_operational)
        self.assertIn("Ninebot Max", repr(scooter))

    def test_bicycle_does_not_consume_energy_isp(self) -> None:
        """Проверка принципа разделения интерфейсов (ISP): велосипед не энергопотребитель."""
        bike = Bicycle(
            inventory_number="BK-01",
            name="Classic Bike",
            simplicity_score=7,
            gear_count=21,
        )
        self.assertIsInstance(bike, IVehicle)
        self.assertIsInstance(bike, IInventoryItem)
        self.assertNotIsInstance(bike, IEnergyConsumer)
        self.assertEqual(bike.gear_count, 21)
        self.assertEqual(bike.vehicle_type, "Механический велосипед")

    def test_electric_bicycle_properties(self) -> None:
        ebike = ElectricBicycle(
            inventory_number="EB-01",
            name="Volt Speed",
            simplicity_score=5,
            daily_energy_kwh=2.0,
            motor_power_w=350,
        )
        self.assertIsInstance(ebike, IVehicle)
        self.assertIsInstance(ebike, IEnergyConsumer)
        self.assertEqual(ebike.motor_power_w, 350)
        self.assertEqual(ebike.daily_energy_kwh, 2.0)

    def test_novice_suitability_boundary_rule(self) -> None:
        """
        Фиксация правила ТЗ: 'при значении >= 6 устройство можно выдавать новичкам'.
        Проверяются значения от 1 до 10, особое внимание на границу 5 и 6.
        """
        cases = [
            (1, False),
            (4, False),
            (5, False),  # Граничное значение 5 -> False
            (6, True),   # Граничное значение 6 -> True
            (7, True),
            (10, True),
        ]
        for score, expected in cases:
            with self.subTest(score=score):
                scooter = KickScooter("KS-T", "Test", simplicity_score=score, daily_energy_kwh=1.0)
                self.assertEqual(scooter.is_suitable_for_novice(), expected)

    def test_vehicle_validation_errors(self) -> None:
        with self.assertRaises(ValueError):
            KickScooter("", "Valid Name", 7, 1.0)

        with self.assertRaises(ValueError):
            KickScooter("KS-01", "   ", 7, 1.0)

        with self.assertRaises(ValueError):
            KickScooter("KS-01", "Name", 0, 1.0)

        with self.assertRaises(ValueError):
            KickScooter("KS-01", "Name", 11, 1.0)

        with self.assertRaises(ValueError):
            KickScooter("KS-01", "Name", 7, -0.5)

        with self.assertRaises(ValueError):
            Bicycle("BK-01", "Name", 7, gear_count=0)

        with self.assertRaises(ValueError):
            ElectricBicycle("EB-01", "Name", 7, 1.0, motor_power_w=0)


class TestItemsModels(unittest.TestCase):
    """Тестирование доменных моделей вещей и оборудования."""

    def test_helmet_properties(self) -> None:
        helmet = Helmet("HLM-01", "Шлем город", size="L")
        self.assertIsInstance(helmet, IInventoryItem)
        self.assertNotIsInstance(helmet, IEnergyConsumer)
        self.assertEqual(helmet.inventory_number, "HLM-01")
        self.assertEqual(helmet.item_category, "Экипировка")
        self.assertEqual(helmet.size, "L")
        self.assertIn("HLM-01", repr(helmet))

    def test_dock_station_properties(self) -> None:
        dock = DockStation("DCK-01", "Станция Мясницкая", slots_count=8, daily_energy_kwh=3.2)
        self.assertIsInstance(dock, IInventoryItem)
        self.assertIsInstance(dock, IEnergyConsumer)
        self.assertEqual(dock.slots_count, 8)
        self.assertEqual(dock.daily_energy_kwh, 3.2)
        self.assertEqual(dock.item_category, "Инфраструктура")

    def test_charging_cabinet_properties(self) -> None:
        cabinet = ChargingCabinet("CHG-01", "Шкаф ФКН", battery_slots=16, daily_energy_kwh=12.5)
        self.assertIsInstance(cabinet, IInventoryItem)
        self.assertIsInstance(cabinet, IEnergyConsumer)
        self.assertEqual(cabinet.battery_slots, 16)
        self.assertEqual(cabinet.daily_energy_kwh, 12.5)
        self.assertEqual(cabinet.item_category, "Зарядное оборудование")

    def test_item_validation_errors(self) -> None:
        with self.assertRaises(ValueError):
            Helmet("", "Helmet")

        with self.assertRaises(ValueError):
            DockStation("DCK-01", "Dock", slots_count=0)

        with self.assertRaises(ValueError):
            ChargingCabinet("CHG-01", "Cabinet", battery_slots=0)


class TestEmployeeModel(unittest.TestCase):
    """Тестирование сущности сотрудника (не ставится на баланс!)."""

    def test_employee_is_not_inventory_item(self) -> None:
        emp = Employee("EMP-01", "Алексей Смирнов", "Инженер")
        self.assertEqual(emp.staff_id, "EMP-01")
        self.assertEqual(emp.full_name, "Алексей Смирнов")
        self.assertEqual(emp.position, "Инженер")
        self.assertNotIsInstance(emp, IInventoryItem)
        self.assertIn("Алексей Смирнов", repr(emp))

    def test_employee_validation(self) -> None:
        with self.assertRaises(ValueError):
            Employee("", "Name", "Role")
        with self.assertRaises(ValueError):
            Employee("EMP-01", "", "Role")


if __name__ == "__main__":
    unittest.main()
