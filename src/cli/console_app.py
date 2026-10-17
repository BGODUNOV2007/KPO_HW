import sys
from typing import Optional
from src.services.fleet_service import FleetService
from src.models.vehicle import KickScooter, Bicycle, ElectricBicycle
from src.models.items import Helmet, DockStation, ChargingCabinet
from src.models.employee import Employee
from src.interfaces.energy import IEnergyConsumer


class ConsoleApp:
    """
    Консольное приложение для управления парком кикшеринга «ВышКат».
    Обеспечивает интерактивный режим и автоматический демонстрационный сценарий (Demo Tour).
    """

    def __init__(self, fleet_service: FleetService) -> None:
        self._fleet = fleet_service

    def run_demo_scenario(self) -> None:
        """
        Демонстрационный сценарий, закрывающий все функциональные требования ТЗ:
        1. Добавление нового ТС в парк
        2. Техосмотр перед приёмкой (успех и отклонение)
        3. Расчёт суммарного суточного энергопотребления
        4. Фильтрация устройств для новичков (простота >= 6)
        5. Учёт вещей на балансе и вывод инвентарных номеров
        6. Архитектурная демонстрация: сотрудник не ставится на баланс!
        """
        print("\n" + "=" * 70)
        print("🛴 ДЕМОНСТРАЦИОННЫЙ СЦЕНАРИЙ СЕРВИСА «ВЫШКАТ» (НИУ ВШЭ) 🛴")
        print("=" * 70)

        # 1 & 2. Добавление техники и техосмотр
        print("\n[ШАГ 1] Добавление исправного электросамоката 'Ninebot Max HSE-Edition'")
        scooter_ok = KickScooter(
            inventory_number="KS-001",
            name="Ninebot Max HSE-Edition",
            simplicity_score=8,
            daily_energy_kwh=1.8,
            is_operational=True,
        )
        res1 = self._fleet.admit_vehicle(scooter_ok)
        print(f" -> Вердикт техосмотра: {res1.message}")
        print(f" -> Результат зачисления: {'УСПЕШНО' if res1.success else 'ОТКЛОНЕНО'}")

        print("\n[ШАГ 2] Попытка добавления НЕИСПРАВНОГО электросамоката 'Xiaomi Pro Defect'")
        scooter_broken = KickScooter(
            inventory_number="KS-002",
            name="Xiaomi Pro Defect",
            simplicity_score=7,
            daily_energy_kwh=1.5,
            is_operational=False,
        )
        res2 = self._fleet.admit_vehicle(scooter_broken)
        print(f" -> Вердикт техосмотра: {res2.message}")
        print(f" -> Результат зачисления: {'УСПЕШНО' if res2.success else 'ОТКЛОНЕНО (в парк не допущен)'}")

        print("\n[ШАГ 3] Добавление механического велосипеда (не потребляет энергию) и электровелосипеда")
        bike = Bicycle(
            inventory_number="BK-101",
            name="Forward City Classic",
            simplicity_score=9,
            gear_count=7,
            is_operational=True,
        )
        ebike = ElectricBicycle(
            inventory_number="EB-201",
            name="Volteco CyberBike",
            simplicity_score=5,  # Сложный для новичка (< 6)
            daily_energy_kwh=2.4,
            motor_power_w=350,
            is_operational=True,
        )
        res3 = self._fleet.admit_vehicle(bike)
        res4 = self._fleet.admit_vehicle(ebike)
        print(f" -> Велосипед {bike.inventory_number}: {res3.message}")
        print(f" -> Электровелосипед {ebike.inventory_number}: {res4.message}")

        # 5. Учёт вещей на балансе
        print("\n[ШАГ 4] Постановка вещей и инфраструктуры на баланс парка")
        helmet1 = Helmet(inventory_number="HLM-01", name="Шлем защитный Urban", size="M")
        helmet2 = Helmet(inventory_number="HLM-02", name="Шлем защитный Urban Pro", size="L")
        dock = DockStation(
            inventory_number="DCK-01",
            name="Док-станция 'Покровский бульвар'",
            slots_count=10,
            daily_energy_kwh=3.5,
        )
        charging = ChargingCabinet(
            inventory_number="CHG-01",
            name="Зарядный шкаф аккумуляторов ФКН",
            battery_slots=12,
            daily_energy_kwh=14.0,
        )

        for item in [helmet1, helmet2, dock, charging]:
            self._fleet.admit_item(item)
            print(f" -> На баланс поставлена вещь: [{item.item_category}] {item.name} (#{item.inventory_number})")

        # Демонстрация правила: сотрудники на баланс не ставятся
        print("\n[ШАГ 5] Демонстрация правила ТЗ: 'Сотрудники на баланс не ставятся'")
        employee = Employee(staff_id="EMP-42", full_name="Иван Петров", position="Техник службы сервиса")
        try:
            self._fleet.admit_item(employee)  # type: ignore
        except TypeError as ex:
            print(f" -> Защита модели сработала успешно: {ex}")

        # 3. Суммарное энергопотребление
        print("\n[ШАГ 6] Отчёт по суточному энергопотреблению парка")
        total_energy = self._fleet.get_total_daily_energy_consumption()
        print(f" -> ⚡ СУММАРНОЕ СУТОЧНОЕ ЭНЕРГОПОТРЕБЛЕНИЕ: {total_energy:.2f} кВт·ч")
        print("    Детализация по потребителям:")
        for item, kwh in self._fleet.get_energy_breakdown():
            print(f"    - [{item.item_category}] {item.name} (#{item.inventory_number}): {kwh:.2f} кВт·ч/сут")

        # 4. Список для новичков
        print("\n[ШАГ 7] Список прокатной техники для новичков (простота >= 6)")
        novice_vehicles = self._fleet.get_novice_friendly_vehicles()
        print(f" -> Найдено подходящих единиц: {len(novice_vehicles)}")
        for v in novice_vehicles:
            print(f"    - [{v.vehicle_type}] {v.name} (#{v.inventory_number}), оценка простоты: {v.simplicity_score}/10")

        # 5. Вывод наименований и инвентарных номеров всех объектов
        print("\n[ШАГ 8] Полный реестр инвентаря на балансе парка «ВышКат»")
        all_inventory = self._fleet.get_all_inventory()
        print(f"{'№':<4} | {'Инв. номер':<12} | {'Категория':<20} | {'Наименование'}")
        print("-" * 70)
        for idx, item in enumerate(all_inventory, 1):
            print(f"{idx:<4} | {item.inventory_number:<12} | {item.item_category:<20} | {item.name}")

        # Итоги
        summary = self._fleet.get_fleet_summary()
        print("\n" + "=" * 70)
        print("📊 СВОДНЫЙ ИТОГ:")
        print(f"   • Активный транспорт: {summary.total_vehicles} ед.")
        print(f"   • Вещи и инфраструктура на балансе: {summary.total_items} ед.")
        print(f"   • Всего объектов инвентаря: {summary.total_inventory_units} ед.")
        print(f"   • Суточное энергопотребление: {summary.total_daily_energy_kwh:.2f} кВт·ч")
        print(f"   • Доступно новичкам: {summary.novice_suitable_count} ед.")
        print("=" * 70)
        print("✅ Демонстрационный сценарий завершён успешно!\n")

    def run_interactive(self) -> None:
        """Интерактивное консольное меню пользователя."""
        while True:
            print("\n" + "=" * 50)
            print("🛴 СЕРВИС КИКШЕРИНГА «ВЫШКАТ» (НИУ ВШЭ) 🛴")
            print("=" * 50)
            print("1. ➕ Принять транспорт в парк (с техосмотром)")
            print("2. 📦 Поставить вещь/оборудование на баланс")
            print("3. ⚡ Отчёт по энергопотреблению парка")
            print("4. 🔰 Список техники для новичков (простота >= 6)")
            print("5. 📋 Полный реестр инвентаря (вся техника и вещи)")
            print("6. 📊 Сводная статистика флота")
            print("7. 🚀 Запустить полный демонстрационный сценарий (Demo)")
            print("0. 🚪 Выход")
            print("=" * 50)

            choice = input("Выберите пункт меню [0-7]: ").strip()

            if choice == "1":
                self._ui_admit_vehicle()
            elif choice == "2":
                self._ui_admit_item()
            elif choice == "3":
                self._ui_show_energy()
            elif choice == "4":
                self._ui_show_novice()
            elif choice == "5":
                self._ui_show_inventory()
            elif choice == "6":
                self._ui_show_summary()
            elif choice == "7":
                self.run_demo_scenario()
            elif choice == "0":
                print("Завершение работы. До встречи в «ВышКат»!")
                break
            else:
                print("❌ Неверный ввод, повторите попытку.")

    def _ui_admit_vehicle(self) -> None:
        print("\n--- Добавление транспортного средства ---")
        print("1. Электросамокат")
        print("2. Механический велосипед")
        print("3. Электровелосипед")
        t_choice = input("Выберите тип [1-3]: ").strip()

        inv = input("Инвентарный номер (например, KS-100): ").strip()
        if not inv:
            print("❌ Инвентарный номер обязателен!")
            return

        name = input("Наименование модели: ").strip()
        if not name:
            print("❌ Наименование обязательно!")
            return

        try:
            score = int(input("Оценка простоты для новичка (1-10): ").strip())
            if not (1 <= score <= 10):
                print("❌ Оценка должна быть от 1 до 10!")
                return
        except ValueError:
            print("❌ Ошибка ввода числа!")
            return

        is_op_input = input("Транспорт технически исправен? (д/н) [по умолч. д]: ").strip().lower()
        is_op = is_op_input not in ("н", "нет", "n", "no")

        vehicle = None
        try:
            if t_choice == "1":
                energy = float(input("Суточный расход энергии (кВт·ч, например 1.8): ").strip())
                vehicle = KickScooter(inv, name, score, energy, is_operational=is_op)
            elif t_choice == "2":
                gears = int(input("Количество передач (например, 7): ").strip() or "7")
                vehicle = Bicycle(inv, name, score, gear_count=gears, is_operational=is_op)
            elif t_choice == "3":
                energy = float(input("Суточный расход энергии (кВт·ч, например 2.2): ").strip())
                power = int(input("Мощность мотора (Вт, например 250): ").strip() or "250")
                vehicle = ElectricBicycle(inv, name, score, energy, motor_power_w=power, is_operational=is_op)
            else:
                print("❌ Неизвестный тип транспорта.")
                return
        except ValueError as e:
            print(f"❌ Ошибка валидации параметров: {e}")
            return

        result = self._fleet.admit_vehicle(vehicle)
        if result.success:
            print(f"✅ {result.message}")
        else:
            print(f"⚠️ Отклонено: {result.message}")

    def _ui_admit_item(self) -> None:
        print("\n--- Постановка вещи на баланс ---")
        print("1. Защитный шлем")
        print("2. Док-станция")
        print("3. Зарядный шкаф")
        i_choice = input("Выберите тип [1-3]: ").strip()

        inv = input("Инвентарный номер (например, HLM-01): ").strip()
        name = input("Наименование: ").strip()

        try:
            if i_choice == "1":
                size = input("Размер (S/M/L) [по умолч. M]: ").strip() or "M"
                item = Helmet(inv, name, size=size)
            elif i_choice == "2":
                slots = int(input("Количество слотов: ").strip())
                energy = float(input("Суточный расход энергии (кВт·ч): ").strip() or "3.0")
                item = DockStation(inv, name, slots_count=slots, daily_energy_kwh=energy)
            elif i_choice == "3":
                bays = int(input("Количество ячеек под аккумуляторы: ").strip())
                energy = float(input("Суточный расход энергии (кВт·ч): ").strip() or "15.0")
                item = ChargingCabinet(inv, name, battery_slots=bays, daily_energy_kwh=energy)
            else:
                print("❌ Неизвестный тип вещи.")
                return

            self._fleet.admit_item(item)
            print(f"✅ Вещь '{name}' (#{inv}) успешно поставлена на баланс.")
        except Exception as e:
            print(f"❌ Ошибка: {e}")

    def _ui_show_energy(self) -> None:
        print("\n--- Отчёт по суточному энергопотреблению ---")
        total = self._fleet.get_total_daily_energy_consumption()
        print(f"⚡ Суммарный расход энергии парка: {total:.2f} кВт·ч/сут")
        breakdown = self._fleet.get_energy_breakdown()
        if not breakdown:
            print("   (В парке нет активных потребителей энергии)")
        else:
            for item, kwh in breakdown:
                print(f"   • [{item.item_category}] {item.name} (#{item.inventory_number}): {kwh:.2f} кВт·ч")

    def _ui_show_novice(self) -> None:
        print("\n--- Техника для новичков (простота >= 6) ---")
        novices = self._fleet.get_novice_friendly_vehicles()
        if not novices:
            print("Подходящей техники для новичков не найдено.")
            return
        for v in novices:
            print(f"   • [{v.vehicle_type}] {v.name} (#{v.inventory_number}) — простота: {v.simplicity_score}/10")

    def _ui_show_inventory(self) -> None:
        print("\n--- Полный реестр инвентаря на балансе ---")
        items = self._fleet.get_all_inventory()
        if not items:
            print("Реестр пуст.")
            return
        print(f"{'№':<4} | {'Инв. номер':<12} | {'Категория':<20} | {'Наименование'}")
        print("-" * 65)
        for idx, item in enumerate(items, 1):
            print(f"{idx:<4} | {item.inventory_number:<12} | {item.item_category:<20} | {item.name}")

    def _ui_show_summary(self) -> None:
        print("\n--- Сводка по флоту «ВышКат» ---")
        s = self._fleet.get_fleet_summary()
        print(f"• Транспортных средств: {s.total_vehicles}")
        print(f"• Вещей на балансе: {s.total_items}")
        print(f"• Всего инвентарных единиц: {s.total_inventory_units}")
        print(f"• Суточное энергопотребление: {s.total_daily_energy_kwh:.2f} кВт·ч")
        print(f"• Доступно новичкам: {s.novice_suitable_count}")
