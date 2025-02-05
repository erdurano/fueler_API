from ninja import Schema
from collections import namedtuple
from .models import FuelStation

location = namedtuple("location", ["latitude", "longitude"])


class Location(Schema):
    latitude: float = -34.456
    longitude: float = 12.567


class StartStopPair(Schema):
    start: Location =  Location(longitude=-73.99874335700979, latitude= 40.70951739405125)
    end: Location = Location(longitude=-118.11802966659334, latitude=34.0469989651079)


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
