import polyline
import folium
import dotenv
import requests
import os

dotenv.load_dotenv()

polyline_code = "ghrlHir~s@?BIC{ELgDo@aBa@}@I?sB?k@?S@o@@sB?_JgAJgHt@I@]iHC?"


polyline_decoded = polyline.decode(polyline_code)
map = folium.Map()

folium.PolyLine((polyline_decoded), tooltip="route").add_to(map)

print(polyline_decoded)


map.save("map.html")

response = requests.post(
    "https://api.openrouteservice.org/v2/directions/driving-car/json",
    headers={"Authorization": str(os.getenv("OPENROUTE_KEY"))},
    json={
        "coordinates": [[8.681495, 49.41461], [8.686507, 49.41943]],
        "units": "mi",
    },
)

json = response.json()

print(response.json())
