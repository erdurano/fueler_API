import os

import dotenv
import requests
import polyline

from .schemas import StartStopPair
from .other.example_jsons import new_york_to_la

dotenv.load_dotenv()


class FuelService:

    @staticmethod
    def get_fuel_data(route_dict: dict):
        return {"usd_gas_expended": 0, "fuel_stops": []}


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
                (stop["location"]["latitude"], stop["location"]["longitude"]),
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
        # request_json = {
        #     "coordinates": [
        #         [start_stop.start.latitude, start_stop.start.longitude],
        #         [start_stop.end.latitude, start_stop.end.longitude],
        #     ],
        #     "units": "mi",
        # }
        # response = requests.post(
        #     url=self.__base_url, headers=self.__headers, json=request_json
        # )

        # if response.status_code != 200:
        #     raise Exception

        # response_dict = response.json()

        response_dict = new_york_to_la

        # client = openrouteservice.Client(key=str(os.getenv("OPENROUTE_KEY")))

        # response_dict = directions(
        #     client=client,
        #     coordinates=[
        #         [start_stop.start.latitude, start_stop.start.longitude],
        #         [start_stop.end.latitude, start_stop.end.longitude],
        #     ],
        # )

        if response_dict["routes"][0]["summary"]["distance"] >= 500:
            fuel_data = FuelService.get_fuel_data(response_dict)
        else:
            fuel_data = {"total_fuel_usd": 0, "fuel_stops": []}

        route_points = polyline.decode(response_dict["routes"][0]["geometry"])

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
