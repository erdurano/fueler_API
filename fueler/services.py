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
    ):
        return "index.html"


class RouteService:
    __base_url = "https://api.openrouteservice.org/v2/directions/driving-car/json"
    __headers = {"Authorization": str(os.getenv("OPENROUTE_KEY"))}

    def get_route_data(self, start_stop: StartStopPair):
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

        if response_dict["routes"][0]["summary"]["distance"] >= 500:
            fuel_data = FuelService.get_fuel_data(response_dict)
        else:
            fuel_data = {}

        route_points = polyline.decode(response_dict["routes"][0]["geometry"])

        map_url = MapService.get_map(
            response_dict["bbox"], route_points, fuel_data.get("fuel_stops", [])
        )
