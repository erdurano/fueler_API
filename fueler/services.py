from ast import Tuple
import math
import os
from datetime import datetime
from pathlib import Path

import dotenv
import folium
import openrouteservice
import polyline
import requests
from django.conf import settings
from django.db.models import Q
from geopy.distance import distance as geodistance
from openrouteservice.directions import directions

from .models import FuelStation
from .other.example_jsons import new_york_to_la
from .schemas import Location, RouteResponse, StartStopPair, location

dotenv.load_dotenv()


class FuelService:
    max_range_miles: float = 500.0
    miles_per_gallon: float = 10.0
    reserve_miles: float = 150

    def __init__(self):
        self._reset()

    def _reset(self):
        self.range = self.max_range_miles
        self.total_distance_mi = 0
        self.total_duration = 0
        self.usd_gas_expended = 0
        self.route_points: list[tuple[float, float]] = []
        self.direction_steps: list[dict] = []
        self.direction_step: int = 0
        self.fuel_stops: list[FuelStation] = []

    def _fill_up(self, station: FuelStation):
        gallon_to_buy = (self.max_range_miles - self.range) / self.miles_per_gallon
        self.usd_gas_expended += float(station.gallon_price) * gallon_to_buy
        self.range = self.max_range_miles
        self.fuel_stops.append(station)

    @property
    def _location(self) -> tuple[float, float]:
        if not self.direction_steps:
            return (0.0, 0.0)
        else:
            return self.route_points[
                self.direction_steps[self.direction_step]["way_points"][0]
            ]

    @property
    def _next_location(self) -> tuple[float, float]:
        if not self.direction_steps:
            return (0.0, 0.0)
        else:
            return self.route_points[
                self.direction_steps[self.direction_step]["way_points"][1]
            ]

    def _get_bounding_box(self, location, radius):
        # 1 degree of latitude is approximately 69 miles
        lat_distance = radius / 69.0

        # 1 degree of longitude varies based on latitude
        lon_distance = radius / (69.0 * math.cos(math.radians(location[0])))

        min_lat = location[0] - lat_distance
        max_lat = location[0] + lat_distance
        min_lon = location[1] - lon_distance
        max_lon = location[1] + lon_distance

        return min_lat, max_lat, min_lon, max_lon

    def _find_optimal_station(self):
        for point in self.route_points[
            self.direction_steps[self.direction_step]["way_points"][0] :
        ]:
            min_lat, max_lat, min_lon, max_lon = self._get_bounding_box(
                point, self.reserve_miles
            )
            if query := FuelStation.objects.filter(
                latitude__range=(min_lat, max_lat), longitude__range=(min_lon, max_lon)
            ).order_by("gallon_price"):
                return query[0]

    def _distance_to_station(self, station: FuelStation):
        return geodistance(self._location, (station.latitude, station.longitude)).miles

    def _distance_from_station_to_next(self, station: FuelStation):
        return geodistance(
            self._next_location, (station.latitude, station.longitude)
        ).miles

    def _distance_to_next_location(self):
        return self.direction_steps[self.direction_step]["distance"]

    @property
    def _step_duration(self):
        return self.direction_steps[self.direction_step]["duration"]

    def _advance(self):
        self.total_duration += self._step_duration
        self.total_distance_mi += self._distance_to_next_location()
        self.range -= self._distance_to_next_location()
        self.direction_step += 1

    def _advance_through_fuel_stop(self, station: FuelStation):
        self.total_duration += self._step_duration
        self.total_distance_mi += self._distance_to_station(station)
        self.range -= self._distance_to_station(station)
        self._fill_up(station)
        self.total_distance_mi += self._distance_from_station_to_next(station)
        self.range -= self._distance_from_station_to_next(station)
        self.direction_step += 1

    def _fit_fuel_stops_to_schema(self):
        to_deliver = []
        for stop in self.fuel_stops:
            to_deliver.append(
                {
                    "opis_id": stop.opis_id,
                    "name": stop.name,
                    "address": stop.address,
                    "city": stop.city,
                    "state": stop._state,
                    "location": {
                        "latitude": stop.latitude,
                        "longitude": stop.longitude,
                    },
                }
            )
        return to_deliver

    def get_fuel_data(
        self, direction_steps: list, route_points: list[tuple[float, float]]
    ):
        self._reset()
        self.direction_steps = direction_steps
        self.route_points = route_points
        for step in direction_steps:
            if (
                self.range < self.reserve_miles
                or self._distance_to_next_location() > self.range
            ):
                station = self._find_optimal_station()
                self._advance_through_fuel_stop(station)
            else:
                self._advance()
        return {
            "usd_gas_expended": self.usd_gas_expended,
            "fuel_stops": self._fit_fuel_stops_to_schema(),
        }


class MapService:

    @staticmethod
    def get_map(
        bounding_box: list[float],
        route_geometry: list[tuple[float, float]],
        fuel_stops: list[dict],
        request,
    ):
        map_id = str(datetime.now())

        file_path = Path(settings.MAPS_DIRECTORY) / f"{map_id}.html"

        min_lon, min_lat, max_lon, max_lat = bounding_box
        center_lat = (max_lat + min_lat) / 2
        center_lon = (max_lon + min_lon) / 2

        map = folium.Map(
            location=[center_lat, center_lon],
            min_lon=min_lon,
            min_lat=min_lat,
            max_lon=max_lon,
            max_lat=max_lat,
            max_bounds=True,
            zoom_start=5,
        )

        for stop in fuel_stops:
            folium.Marker(
                (
                    float(stop["location"]["latitude"]),
                    float(stop["location"]["longitude"]),
                ),
                tooltip="station",
                popup=stop["name"],
                icon=folium.Icon(icon="gas-pump"),
            ).add_to(map)

        folium.PolyLine(route_geometry, tooltip="route").add_to(map)

        map.save(file_path)
        return f"{request.META['HTTP_HOST']}/maps/{map_id}/"


class RouteService:
    __base_url = "https://api.openrouteservice.org/v2/directions/driving-car/json"
    __headers = {"Authorization": str(os.getenv("OPENROUTE_KEY"))}

    def get_route_data(self, start_stop: StartStopPair, request):
        request_json = {
            "coordinates": [
                [start_stop.start.longitude, start_stop.start.latitude],
                [start_stop.end.longitude, start_stop.end.latitude],
            ],
            "units": "mi",
        }
        response = requests.post(
            url=self.__base_url, headers=self.__headers, json=request_json
        )

        if response.status_code != 200:
            raise Exception

        response_dict = response.json()

        # response_dict = new_york_to_la

        # client = openrouteservice.Client(key=str(os.getenv("OPENROUTE_KEY")))

        # response_dict = directions(
        #     client=client,
        #     coordinates=[
        #         [start_stop.start.latitude, start_stop.start.longitude],
        #         [start_stop.end.latitude, start_stop.end.longitude],
        #     ],
        # )
        route_points = polyline.decode(response_dict["routes"][0]["geometry"])
        direction_steps = response_dict["routes"][0]["segments"][0]["steps"]

        if response_dict["routes"][0]["summary"]["distance"] >= 500:
            fuel_data = FuelService().get_fuel_data(direction_steps, route_points)
        else:
            fuel_data = {"total_fuel_usd": 0, "fuel_stops": []}

        map_url = MapService.get_map(
            response_dict["bbox"],
            route_points,
            fuel_data.get("fuel_stops", []),
            request,
        )

        duration = response_dict["routes"][0]["summary"]["duration"]

        return self._get_route_schema(route_points, fuel_data, map_url, duration)

    @staticmethod
    def _get_route_schema(route_points, fuel_data, map_url, duration):
        route_start = Location(
            latitude=route_points[0][0], longitude=route_points[0][1]
        )
        route_end = Location(
            latitude=route_points[-1][0], longitude=route_points[-1][1]
        )
        return {
            "start": route_start,
            "end": route_end,
            "duration": duration,
            "map_url": map_url,
            "fuel_data": fuel_data,
            "route_points": route_points,
        }
