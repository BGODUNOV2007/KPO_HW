from src.interfaces.inventory import IInventoryItem
from src.interfaces.energy import IEnergyConsumer
from src.interfaces.vehicle import IVehicle
from src.interfaces.service_center import IServiceCenter, InspectionResult
from src.interfaces.repository import IFleetRepository

__all__ = [
    "IInventoryItem",
    "IEnergyConsumer",
    "IVehicle",
    "IServiceCenter",
    "InspectionResult",
    "IFleetRepository",
]
