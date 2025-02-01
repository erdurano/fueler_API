# Manually written to insert fuel stops to db


import csv
from pathlib import Path
from typing import Any

from django.db import migrations, models
from fueler.models import City, FuelStation

data_path = Path(__file__).parent.parent.parent / "data"
provided_file_name = "fuel-prices-for-be-assessment.csv"


def load_file(file_name: str):
    """Removes duplicate fuel stops. Holds smaller fuel prices for each stop for calculating fuel prices further down. Returns a dictionary which keys are OPIS TruckStop ID's."""
    price_list: list[dict[str, Any[str, int, float]]] = []
    with open((data_path / file_name).absolute()) as file:
        reader = csv.reader(file, dialect="excel")
        for index, row in enumerate(reader):
            if index > 0:
                item = dict()
                item["opis_id"] = int(row[0])
                item["name"] = row[1].strip()
                item["address"] = row[2].strip()
                item["city"] = row[3].strip()
                item["state"] = row[4].strip()
                item["rack_id"] = row[5].strip()
                item["gallon_price"] = float(row[6])
                price_list.append(item)
    return price_list


def load_fuel_stops(apps, schema_editor):

    csv_list = load_file(provided_file_name)

    for csv_fuel_station in csv_list:
        try:
            city = City.objects.get(
                name=csv_fuel_station["city"], state=csv_fuel_station["state"]
            )
        except City.DoesNotExist:
            city = City(name=csv_fuel_station["city"], state=csv_fuel_station["state"])
            city.save()
        try:
            station = FuelStation.objects.get(name=csv_fuel_station["name"])
            if csv_fuel_station["gallon_price"] < station.gallon_price:
                station.gallon_price = csv_fuel_station["gallon_price"]
                station.save()
        except FuelStation.DoesNotExist:
            station = FuelStation(
                opis_id=csv_fuel_station["opis_id"],
                name=csv_fuel_station["name"],
                address=csv_fuel_station["address"],
                city=city,
                rack_id=csv_fuel_station["rack_id"],
                gallon_price=csv_fuel_station["gallon_price"],
            )

            station.save()


def remove_fuel_stops(apps, schema_editor):
    FuelStation = apps.get_model("fueler", "FuelStation")
    FuelStation.objects.all().delete()


class Migration(migrations.Migration):

    dependencies = [
        ("fueler", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(load_fuel_stops),
    ]
