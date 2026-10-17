class Employee:
    """
    Сотрудник службы эксплуатации сервиса «ВышКат».
    По ТЗ: сотрудники НЕ ставятся на баланс и не являются инвентарными объектами!
    Класс представлен в доменной модели для демонстрации разделения сущностей
    и архитектурного ответа на вопрос о добавлении сотрудников в систему.
    """

    def __init__(self, staff_id: str, full_name: str, position: str) -> None:
        if not staff_id or not staff_id.strip():
            raise ValueError("ID сотрудника не может быть пустым.")
        if not full_name or not full_name.strip():
            raise ValueError("ФИО сотрудника не может быть пустым.")

        self.staff_id = staff_id.strip()
        self.full_name = full_name.strip()
        self.position = position.strip()

    def __repr__(self) -> str:
        return f"<Сотрудник {self.staff_id}: {self.full_name} ({self.position})>"
