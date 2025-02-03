from ninja import Schema
from collections import namedtuple

location = namedtuple("location", ["latitude", "longitude"])


class Location(Schema):
    latitude: float = -34.456
    longitude: float = 12.567


class StartStopPair(Schema):
    start: Location
    end: Location


class FuelStop(Schema):
    opis_id: str
    name: str
    address: str
    city: str
    state: str
    location: Location


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
