# Manually written to insert fuel stops to db


import csv
from pathlib import Path

from django.db import migrations, models
from fueler.models import City, FuelStation

data_path = Path(__file__).parent.parent.parent / "data"
provided_file_name = "fuel-prices-for-be-assessment.csv"


def sanitize_data(file_name: str):
    """Removes duplicate fuel stops. Holds smaller fuel prices for each stop for calculating fuel prices further down. Returns a dictionary which keys are OPIS TruckStop ID's."""
    price_dict: dict[int, dict] = {}
    with open((data_path / file_name).absolute()) as file:
        reader = csv.reader(file, dialect="excel")
        for index, row in enumerate(reader):
            if index > 0:
                item = dict()
                print(row)
                opis_id = int(row[0])
                item["name"] = row[1].strip()
                item["address"] = row[2].strip()
                item["city"] = row[3].strip()
                item["state"] = row[4].strip()
                item["rack_id"] = row[5].strip()
                gallon_price = float(row[6])
                try:
                    if gallon_price < price_dict[opis_id]["gallon_price"]:
                        item["gallon_price"] = gallon_price
                    else:
                        item["gallon_price"] = price_dict[opis_id]["gallon_price"]
                except KeyError:
                    item["gallon_price"] = gallon_price

                price_dict[opis_id] = item

    return price_dict


def load_fuel_stops(apps, schema_editor):

    csv_dict = sanitize_data(provided_file_name)

    for opis_id, csv_fuel_station in csv_dict.items():
        try:
            city = City.objects.get(
                name=csv_fuel_station["city"], state=csv_fuel_station["state"]
            )
        except City.DoesNotExist:
            city = City(name=csv_fuel_station["city"], state=csv_fuel_station["state"])
            city.save()
        try:
            station = FuelStation.objects.get(opis_id=opis_id)
            if csv_fuel_station["gas_price"] < station.gas_price:
                station.gas_price = csv_fuel_station["gas_price"]
                station.save()
        except FuelStation.DoesNotExist:
            station = FuelStation(
                opis_id=opis_id,
                name=csv_fuel_station["name"],
                address=csv_fuel_station["address"],
                city=city,
                rack_id=csv_fuel_station["rack_id"],
                gas_price=csv_fuel_station["gallon_price"],
            )

            station.save()


def remove_fuel_stops(apps, schema_editor):
    FuelStation = apps.get_model("fueler", "FuelStation")
    FuelStation.objects.all().delete()


class Migration(migrations.Migration):

    dependencies = [
        ("fueler", "0003_auto_20250201_1021"),
    ]

    operations = [
        migrations.RunPython(load_fuel_stops),
    ]
