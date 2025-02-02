from ninja import NinjaAPI, Query
from .schemas import RouteResponse, StartStopPair

api = NinjaAPI()


@api.get(
    "route/",
    description="""
Start-end address or start-end locations are required as pairs.

Examples:

/api/route?start_location=-12.95678,30.06278&end_location=32.12345,16.5793
""",
    response=RouteResponse,
)
def route_by_query(
    request,
    start_location: Query[str] = "0,0",
    end_location: Query[str] = "0,0",
):
    return {
        "start": {"latitude": -34.456, "longitude": 12.567},
        "end": {"latitude": -34.456, "longitude": 12.567},
        "duration": 0,
        "usd_gas_expended": 0,
        "map_url": "string",
        "route_points": [{"latitude": -34.456, "longitude": 12.567}],
        "fuel_stops": [
            {
                "opis_id": "string",
                "name": "string",
                "address": "string",
                "city": "string",
                "state": "string",
                "location": {"latitude": -34.456, "longitude": 12.567},
            }
        ],
    }


@api.post("route/", response=RouteResponse)
def route_by_request_body(request, start_stop: StartStopPair):
    return {
        "start": {"latitude": -34.456, "longitude": 12.567},
        "end": {"latitude": -34.456, "longitude": 12.567},
        "duration": 0,
        "usd_gas_expended": 0,
        "map_url": "string",
        "route_points": [{"latitude": -34.456, "longitude": 12.567}],
        "fuel_stops": [
            {
                "opis_id": "string",
                "name": "string",
                "address": "string",
                "city": "string",
                "state": "string",
                "location": {"latitude": -34.456, "longitude": 12.567},
            }
        ],
    }
