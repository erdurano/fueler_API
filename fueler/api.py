from ninja import NinjaAPI

api = NinjaAPI()


@api.get(
    "route/",
    description="""
Start-end address or start-end locations are required as pairs.

Examples:

/api/route?start_address=150 Belvedere, Fort Curry, CA&end_address=1130 Trunk St, Milton, PA

/api/route?start_location=-12.95678,30.06278&end_location=32.12345,16.5793
""",
)
def route_by_query(
    request,
    start_address: str = "",
    end_address: str = "",
    start_location: str = "",
    end_location: str = "",
):
    return {
        "start": start_address,
        "end": end_address,
        "start_loc": start_location,
        "end_loc": end_location,
    }


@api.post("route/")
def route_by_request_body(request):
    return "sumthing"
