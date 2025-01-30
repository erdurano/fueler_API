import csv
import pathlib
import os
from dotenv import load_dotenv
from typing import List, Union, Dict, Any, Optional
from requests import post, Response
import json

data_path = pathlib.Path(".") / "data"

load_dotenv()


def sanitize_data():
    """Removes duplicate fuel stops. Holds smaller fuel prices for each stop for calculating fuel prices further down"""
    price_dict: dict[int, dict] = {}
    with open((data_path / "fuel-prices-for-be-assessment.csv").absolute()) as file:
        reader = csv.reader(file, dialect="excel")
        for index, row in enumerate(reader):
            if index > 0:
                item = dict()
                print(row)
                item["name"] = row[1].strip()
                item["address"] = row[2].strip()
                item["city"] = row[3].strip()
                item["state"] = row[4].strip()
                item["rack_id"] = row[5].strip()
                gallon_price = float(row[6])
                try:
                    if gallon_price < price_dict[int(row[0])]["gallon_price"]:
                        item["gallon_price"] = gallon_price
                    else:
                        item["gallon_price"] = price_dict[int(row[0])]["gallon_price"]
                except KeyError:
                    item["gallon_price"] = gallon_price

                price_dict[int(row[0])] = item

    return price_dict


def update_long_lat_data(fuel_stops: Dict[int, Dict[str, Union[int, float, str]]]):
    def chunks(data, size):
        it = iter(data)
        for i in range(0, len(data), size):
            yield {k: data[k] for k in list(it)[:size]}

    def get_reqest_dict(
        batch: Dict[int, Dict[str, Any]]
    ) -> Dict[str, List[Dict[str, str]]]:
        request_dict = {
            "locations": [
                {
                    "location": value["name"],
                    "city": value["city"],
                    "state": value["state"],
                }
                for value in batch.values()
            ]
        }
        return request_dict

    def request_batch_data(
        batch: Dict[str, List[Dict[str, str]]]
    ) -> Optional[Response]:
        batch_request_url_base = "https://www.mapquestapi.com/geocoding/v1/batch"
        response = post(
            url=str.join(
                "", [batch_request_url_base, "?key=", str(os.getenv("MAPQUEST_KEY"))]
            ),
            json=batch,
        )
        if response.status_code == 200:
            return response

    for fuel_stop_batch in chunks(fuel_stops, 100):
        request_dict = get_reqest_dict(fuel_stop_batch)
        response = request_batch_data(request_dict)
        if response is not None:
            response_dict = response.json()
            print(response_dict)
        # TODO: Take lattitude and logitude data from response dict


def print_to_file(fuel_stops: Dict[int, Dict[str, Union[int, float, str]]]):
    rows = []
    with open(
        data_path / "fuel-prices-filtered.csv",
        "w",
    ) as output:
        writer = csv.writer(output, dialect="excel")
        for item in fuel_stops.items():
            row = [
                item[0],
                item[1]["name"],
                item[1]["address"],
                item[1]["city"],
                item[1]["state"],
                item[1]["rack_id"],
                item[1]["gallon_price"],
            ]
            rows.append(row)
        writer.writerows(rows)


def main():
    sanitized_rows = sanitize_data()
    update_long_lat_data(sanitized_rows)
    # print(sanitized_rows)
    # print_to_file(sanitized_rows)


if __name__ == "__main__":

    main()
