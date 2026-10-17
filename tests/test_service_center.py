import unittest
from src.services.service_center import DefaultServiceCenter
from src.models.vehicle import KickScooter, Bicycle


class TestServiceCenter(unittest.TestCase):
    """Тестирование сервиса техосмотра (DefaultServiceCenter)."""

    def setUp(self) -> None:
        self.service_center = DefaultServiceCenter()

    def test_approve_operational_kick_scooter(self) -> None:
        scooter = KickScooter("KS-10", "Segway Ninebot", simplicity_score=7, daily_energy_kwh=1.5, is_operational=True)
        result = self.service_center.inspect(scooter)
        self.assertTrue(result.is_approved)
        self.assertIn("успешно пройден", result.reason)

    def test_reject_broken_kick_scooter(self) -> None:
        scooter = KickScooter("KS-11", "Segway Broken", simplicity_score=7, daily_energy_kwh=1.5, is_operational=False)
        result = self.service_center.inspect(scooter)
        self.assertFalse(result.is_approved)
        self.assertIn("не пройден", result.reason)
        self.assertIn("технические неисправности", result.reason)

    def test_approve_operational_bicycle(self) -> None:
        bike = Bicycle("BK-10", "Stels Navigator", simplicity_score=8, gear_count=18, is_operational=True)
        result = self.service_center.inspect(bike)
        self.assertTrue(result.is_approved)
        self.assertIn("допущено к активной эксплуатации", result.reason)

    def test_reject_vehicle_with_abnormal_energy_consumption(self) -> None:
        scooter = KickScooter("KS-ANOMALY", "Danger Scooter", simplicity_score=6, daily_energy_kwh=55.0, is_operational=True)
        result = self.service_center.inspect(scooter)
        self.assertFalse(result.is_approved)
        self.assertIn("аномально высокий расход", result.reason)


if __name__ == "__main__":
    unittest.main()
