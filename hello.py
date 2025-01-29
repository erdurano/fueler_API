import csv
import pathlib


def main():
    price_dict: dict[int, dict] = {}
    with open(
        "/home/erdurano/Projects/fueler_API/data/fuel-prices-for-be-assessment.csv"
    ) as file:
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

    print(price_dict)
    with open(
        "/home/erdurano/Projects/fueler_API/data/fuel-prices-filtered.csv",
        "w",
    ) as output:
        writer = csv.writer(output, dialect="excel")

        for item in price_dict.items():
            row = [
                item[0],
                item[1]["name"],
                item[1]["address"],
                item[1]["city"],
                item[1]["state"],
                item[1]["rack_id"],
                item[1]["gallon_price"],
            ]
            writer.writerow(row)


if __name__ == "__main__":
    main()
