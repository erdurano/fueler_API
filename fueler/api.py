from ninja import NinjaAPI, Query
from .schemas import RouteResponse, StartStopPair, Location
from .services import RouteService

api = NinjaAPI()


@api.get(
    "route/",
    description="""
Location strings should be a pair of latitude,longitude.

Examples:

/api/route?start_location=-12.95678,30.06278&end_location=32.12345,16.5793
""",
    response=RouteResponse,
)
def route_by_query(
    request,
    start_location: Query[str] = "-73.99874335700979,40.70951739405125",
    end_location: Query[str] = "0,0",
):
    start_lat, start_long = (float(i) for i in start_location.split(","))
    end_lat, end_long = (float(i) for i in end_location.split(","))

    pair = StartStopPair(
        start=Location(latitude=start_lat, longitude=start_long),
        end=Location(latitude=end_lat, longitude=end_long),
    )
    return RouteService().get_route_data(pair, request)


@api.post("route/", response=RouteResponse)
def route_by_request_body(request, start_stop: StartStopPair):
    return RouteService().get_route_data(start_stop, request)
