import inspect
from typing import Any, Callable, Dict, Type, TypeVar, Optional

T = TypeVar("T")


class ServiceNotFoundError(Exception):
    """Исключение при запросе незарегистрированного сервиса."""
    pass


class DIContainer:
    """
    Легковесный и строгий Dependency Injection (DI) контейнер.
    Реализует паттерн Inversion of Control (IoC).
    
    Поддерживает:
    - Регистрацию синглтонов (Singleton)
    - Регистрацию фабрик/новых экземпляров (Transient)
    - Регистрацию готовых экземпляров (Instance), что идеально подходит для подмены Mock/Stub в тестах
    - Автоматическое разрешение зависимостей по аннотациям типов конструктора (__init__)
    """

    def __init__(self) -> None:
        self._services: Dict[Type, Dict[str, Any]] = {}
        self._instances: Dict[Type, Any] = {}

    def register_instance(self, interface: Type[T], instance: T) -> None:
        """
        Зарегистрировать готовый экземпляр (часто используется для Mock/Stub в тестах).
        При повторной регистрации переопределяет (override) существующую зависимость.
        """
        self._services[interface] = {"type": "instance", "value": instance}
        self._instances[interface] = instance

    def register_singleton(
        self,
        interface: Type[T],
        implementation: Optional[Type[T]] = None,
        factory: Optional[Callable[["DIContainer"], T]] = None,
    ) -> None:
        """
        Зарегистрировать сервис с жизненным циклом Singleton (один экземпляр на всё приложение).
        """
        impl = implementation or interface
        self._services[interface] = {
            "type": "singleton",
            "impl": impl,
            "factory": factory,
        }
        # Сбрасываем старый кэшированный инстанс, если был
        if interface in self._instances:
            del self._instances[interface]

    def register_transient(
        self,
        interface: Type[T],
        implementation: Optional[Type[T]] = None,
        factory: Optional[Callable[["DIContainer"], T]] = None,
    ) -> None:
        """
        Зарегистрировать сервис с жизненным циклом Transient (новый экземпляр при каждом resolve).
        """
        impl = implementation or interface
        self._services[interface] = {
            "type": "transient",
            "impl": impl,
            "factory": factory,
        }

    def is_registered(self, interface: Type) -> bool:
        """Проверить регистрацию интерфейса в контейнере."""
        return interface in self._services

    def resolve(self, service_type: Type[T]) -> T:
        """
        Разрешить зависимость: создать или вернуть кэшированный экземпляр,
        рекурсивно разрешая все параметры конструктора.
        """
        if service_type in self._instances:
            return self._instances[service_type]

        if service_type not in self._services:
            # Абстрактные интерфейсы нельзя создать автоматически без регистрации
            if inspect.isabstract(service_type):
                raise ServiceNotFoundError(
                    f"Абстрактный интерфейс {service_type.__name__} не зарегистрирован в DI-контейнере."
                )
            # Если тип является конкретным классом, создаём его
            if inspect.isclass(service_type):
                return self._create_instance(service_type)
            raise ServiceNotFoundError(
                f"Сервис {service_type.__name__} не зарегистрирован в DI-контейнере."
            )

        registration = self._services[service_type]
        reg_type = registration["type"]

        if reg_type == "instance":
            return registration["value"]

        factory = registration.get("factory")
        impl = registration.get("impl")

        if reg_type == "singleton":
            if factory:
                instance = factory(self)
            else:
                instance = self._create_instance(impl)
            self._instances[service_type] = instance
            return instance

        elif reg_type == "transient":
            if factory:
                return factory(self)
            return self._create_instance(impl)

        raise ValueError(f"Неизвестный тип регистрации: {reg_type}")

    def _create_instance(self, cls: Type[T]) -> T:
        """Рекурсивно создаёт экземпляр класса, разрешая зависимости конструктора."""
        if cls.__init__ is object.__init__:
            return cls()

        init_sig = inspect.signature(cls.__init__)
        parameters = list(init_sig.parameters.values())[1:]  # пропускаем self

        resolved_args = {}
        for param in parameters:
            if param.kind in (inspect.Parameter.VAR_POSITIONAL, inspect.Parameter.VAR_KEYWORD):
                continue

            param_type = param.annotation
            if param_type is inspect.Parameter.empty:
                if param.default is not inspect.Parameter.empty:
                    continue
                raise ValueError(
                    f"Параметр '{param.name}' в конструкторе {cls.__name__} не имеет аннотации типа."
                )

            # Рекурсивный resolve параметра
            resolved_args[param.name] = self.resolve(param_type)

        return cls(**resolved_args)


def create_app_container() -> DIContainer:
    """
    Фабрика стандартного DI-контейнера приложения «ВышКат».
    Регистрирует доменные зависимости и собирает граф объектов.
    """
    from src.interfaces.service_center import IServiceCenter
    from src.interfaces.repository import IFleetRepository
    from src.services.service_center import DefaultServiceCenter
    from src.services.fleet_repository import InMemoryFleetRepository
    from src.services.fleet_service import FleetService

    container = DIContainer()

    # Регистрация зависимостей
    container.register_singleton(IFleetRepository, InMemoryFleetRepository)
    container.register_singleton(IServiceCenter, DefaultServiceCenter)
    container.register_singleton(FleetService)

    return container
