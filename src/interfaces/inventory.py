from abc import ABC, abstractmethod


class IInventoryItem(ABC):
    """
    Абстракция для любого инвентаризируемого объекта на балансе парка.
    Соблюдает Interface Segregation Principle (ISP): содержит только атрибуты,
    необходимые для инвентарного учёта.
    """

    @property
    @abstractmethod
    def inventory_number(self) -> str:
        """Уникальный инвентарный номер объекта."""
        pass

    @property
    @abstractmethod
    def name(self) -> str:
        """Понятное наименование объекта."""
        pass

    @property
    @abstractmethod
    def item_category(self) -> str:
        """Категория объекта (например, 'Транспорт', 'Экипировка', 'Инфраструктура')."""
        pass
