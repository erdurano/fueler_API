from ninja import Schema
from collections import namedtuple
from .models import FuelStation

location = namedtuple("location", ["latitude", "longitude"])


class Location(Schema):
    latitude: float = -34.456
    longitude: float = 12.567


class StartStopPair(Schema):
    start: Location
    end: Location


class FuelStop(Schema):
    opis_id: int
    name: str
    address: str
    city: str
    state: str
    location: Location

    @classmethod
    def from_model(cls, instance: FuelStation):
        return cls(
            opis_id=instance.opis_id,
            name=instance.name,
            address=instance.address,
            city=instance.city.name,
            state=instance.city.state,
            location=Location(
                latitude=float(instance.latitude), longitude=float(instance.longitude)
            ),
        )


class FuelData(Schema):
    total_fuel_usd: float = 0
    fuel_stops: list[FuelStop]


class RouteResponse(Schema):
    start: Location
    end: Location
    duration: float
    map_url: str
    route_points: list[Location]
    fuel_data: FuelData
