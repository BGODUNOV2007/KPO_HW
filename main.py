#!/usr/bin/env python3
import sys
import argparse
from src.container.di_container import create_app_container
from src.services.fleet_service import FleetService
from src.cli.console_app import ConsoleApp


def main() -> None:
    parser = argparse.ArgumentParser(
        description="ВышКат — система учёта парка кикшеринга НИУ ВШЭ"
    )
    parser.add_argument(
        "--demo",
        action="store_true",
        help="Запустить автоматический демонстрационный сценарий всех требований ТЗ",
    )
    args = parser.parse_args()
    container = create_app_container()
    fleet_service = container.resolve(FleetService)
    app = ConsoleApp(fleet_service)
    if args.demo:
        app.run_demo_scenario()
    else:
        app.run_interactive()


if __name__ == "__main__":
    main()
