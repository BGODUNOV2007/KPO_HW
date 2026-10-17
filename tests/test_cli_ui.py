import io
import sys
import unittest
from unittest.mock import patch

from src.services.fleet_service import FleetService
from src.services.fleet_repository import InMemoryFleetRepository
from src.services.service_center import DefaultServiceCenter
from src.cli.console_app import ConsoleApp


class TestConsoleAppInteractiveUI(unittest.TestCase):
    """Тестирование интерфейсных методов ConsoleApp."""

    def setUp(self) -> None:
        self.repository = InMemoryFleetRepository()
        self.service_center = DefaultServiceCenter()
        self.fleet_service = FleetService(self.repository, self.service_center)
        self.app = ConsoleApp(self.fleet_service)

    def test_ui_admit_kick_scooter_flow(self) -> None:
        inputs = iter(["1", "KS-UI-1", "Scooter UI", "8", "д", "1.5"])
        with patch("builtins.input", lambda _: next(inputs)):
            self.app._ui_admit_vehicle()

        self.assertEqual(len(self.fleet_service.get_all_vehicles()), 1)
        v = self.fleet_service.get_all_vehicles()[0]
        self.assertEqual(v.inventory_number, "KS-UI-1")

    def test_ui_admit_bicycle_flow(self) -> None:
        inputs = iter(["2", "BK-UI-1", "Bicycle UI", "7", "д", "8"])
        with patch("builtins.input", lambda _: next(inputs)):
            self.app._ui_admit_vehicle()

        self.assertEqual(len(self.fleet_service.get_all_vehicles()), 1)
        self.assertEqual(self.fleet_service.get_all_vehicles()[0].inventory_number, "BK-UI-1")

    def test_ui_admit_electric_bicycle_flow(self) -> None:
        inputs = iter(["3", "EB-UI-1", "EBike UI", "5", "д", "2.0", "300"])
        with patch("builtins.input", lambda _: next(inputs)):
            self.app._ui_admit_vehicle()

        self.assertEqual(len(self.fleet_service.get_all_vehicles()), 1)
        self.assertEqual(self.fleet_service.get_all_vehicles()[0].inventory_number, "EB-UI-1")

    def test_ui_admit_vehicle_validation_empty_inv(self) -> None:
        inputs = iter(["1", "", "Name"])
        captured = io.StringIO()
        old_stdout = sys.stdout
        try:
            sys.stdout = captured
            with patch("builtins.input", lambda _: next(inputs)):
                self.app._ui_admit_vehicle()
        finally:
            sys.stdout = old_stdout

        self.assertIn("Инвентарный номер обязателен", captured.getvalue())

    def test_ui_admit_items_flow(self) -> None:
        inputs_helmet = iter(["1", "HLM-UI", "Шлем UI", "L"])
        with patch("builtins.input", lambda _: next(inputs_helmet)):
            self.app._ui_admit_item()

        inputs_dock = iter(["2", "DCK-UI", "Док UI", "10", "3.5"])
        with patch("builtins.input", lambda _: next(inputs_dock)):
            self.app._ui_admit_item()

        inputs_cab = iter(["3", "CHG-UI", "Шкаф UI", "16", "14.0"])
        with patch("builtins.input", lambda _: next(inputs_cab)):
            self.app._ui_admit_item()

        self.assertEqual(len(self.fleet_service.get_all_items()), 3)

    def test_ui_reports_output(self) -> None:
        captured = io.StringIO()
        old_stdout = sys.stdout
        try:
            sys.stdout = captured
            self.app._ui_show_energy()
            self.app._ui_show_novice()
            self.app._ui_show_inventory()
            self.app._ui_show_summary()
        finally:
            sys.stdout = old_stdout

        output = captured.getvalue()
        self.assertIn("Суммарный расход энергии парка: 0.00", output)
        self.assertIn("Подходящей техники для новичков не найдено", output)
        self.assertIn("Реестр пуст", output)
        self.assertIn("Транспортных средств: 0", output)

    def test_interactive_menu_exit_flow(self) -> None:
        inputs = iter(["0"])
        with patch("builtins.input", lambda _: next(inputs)):
            self.app.run_interactive()


if __name__ == "__main__":
    unittest.main()
