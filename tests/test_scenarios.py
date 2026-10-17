import io
import sys
import unittest
from src.container.di_container import create_app_container
from src.services.fleet_service import FleetService
from src.cli.console_app import ConsoleApp


class TestApplicationScenarios(unittest.TestCase):
    """Интеграционные тесты демонстрационных и сквозных сценариев."""

    def test_demo_scenario_runs_completely_without_errors(self) -> None:
        """
        Проверяет выполнение полного демонстрационного тура,
        закрывающего все 6 требований ТЗ.
        """
        container = create_app_container()
        fleet_service = container.resolve(FleetService)
        app = ConsoleApp(fleet_service)

        captured_output = io.StringIO()
        old_stdout = sys.stdout
        try:
            sys.stdout = captured_output
            app.run_demo_scenario()
        finally:
            sys.stdout = old_stdout

        output = captured_output.getvalue()

        # Проверяем наличие всех ключевых этапов ТЗ
        self.assertIn("[ШАГ 1] Добавление исправного электросамоката", output)
        self.assertIn("[ШАГ 2] Попытка добавления НЕИСПРАВНОГО электросамоката", output)
        self.assertIn("[ШАГ 3] Добавление механического велосипеда", output)
        self.assertIn("[ШАГ 4] Постановка вещей и инфраструктуры на баланс парка", output)
        self.assertIn("[ШАГ 5] Демонстрация правила ТЗ: 'Сотрудники на баланс не ставятся'", output)
        self.assertIn("[ШАГ 6] Отчёт по суточному энергопотреблению парка", output)
        self.assertIn("[ШАГ 7] Список прокатной техники для новичков", output)
        self.assertIn("[ШАГ 8] Полный реестр инвентаря на балансе парка", output)
        self.assertIn("СВОДНЫЙ ИТОГ:", output)
        self.assertIn("Демонстрационный сценарий завершён успешно!", output)

    def test_repository_inventory_integrity_after_scenario(self) -> None:
        """Проверяет целостность данных в сервисе после отработки сценария."""
        container = create_app_container()
        fleet_service = container.resolve(FleetService)
        app = ConsoleApp(fleet_service)

        captured_output = io.StringIO()
        old_stdout = sys.stdout
        try:
            sys.stdout = captured_output
            app.run_demo_scenario()
        finally:
            sys.stdout = old_stdout

        summary = fleet_service.get_fleet_summary()
        self.assertEqual(summary.total_vehicles, 3)
        self.assertEqual(summary.total_items, 4)
        self.assertEqual(summary.total_inventory_units, 7)
        self.assertEqual(summary.novice_suitable_count, 2)


if __name__ == "__main__":
    unittest.main()
