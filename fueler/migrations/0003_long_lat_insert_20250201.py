# Manually written to insert longitude and latitude data for pinning on map


import os

import requests
from django.db import migrations
from dotenv import load_dotenv

from fueler.models import City, FuelStation

load_dotenv()


def query_data_batch(chunk):
    """Gets and updates longitude and lattitude values from MapQuest API"""
    batch_request_url_base = "https://www.mapquestapi.com/geocoding/v1/batch"

    request_dict = {
        "locations": [
            {
                "location": station.name,
                "city": station.city.name,
                "state": station.city.state,
            }
            for station in chunk
        ]
    }

    response = requests.post(
        url=str.join(
            "", [batch_request_url_base, "?key=", str(os.getenv("MAPQUEST_KEY"))]
        ),
        json=request_dict,
    )

    if response.status_code == 200:
        response_dict = response.json()

    location_results = response_dict["results"]

    for item in location_results:
        name = item["providedLocation"]["city"]
        state = item["providedLocation"]["state"]
        print(name, state)
        station = FuelStation.objects.get(
            name=item["providedLocation"]["location"],
            city=City.objects.get(
                name=item["providedLocation"]["city"],
                state=item["providedLocation"]["state"],
            ),
        )
        station.latitude = item["locations"][0]["latLng"]["lat"]
        station.longitude = item["locations"][0]["latLng"]["lng"]
        station.save()


def update_long_lat(apps, schema_editor):

    fuel_station_collection = FuelStation.objects.all()
    batch_size = 100

    for chunk in [
        fuel_station_collection[i : i + batch_size]
        for i in range(0, len(fuel_station_collection), batch_size)
    ]:
        query_data_batch(chunk)


class Migration(migrations.Migration):

    dependencies = [
        ("fueler", "0002_default_fuel_stops_20250201"),
    ]

    operations = [
        migrations.RunPython(update_long_lat),
    ]
