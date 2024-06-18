#!/usr/bin/env python3

import csv
# import sys

filename = "configs/doc8643.csv"
icaos: dict[str, str] = {}
aircraft_categories: dict[str, list[str]] = {}
mediumwakers: list[str] = []
lowwakers: list[str] = []
nowakers: list[str] = []

strangers: list[str] = []

with open(filename, "r") as doc8643:
    doc_content = csv.DictReader(doc8643, delimiter=";", quotechar='"')
    for row in doc_content:
        if row["WTC"] not in ["", "-", "L", "L/M", "M", "H"]:
            strangers.append(str(row))
        if row["WTC"] not in aircraft_categories:
            aircraft_categories[row["WTC"]] = [row["Type Designator"]]
        else:
            if row["Type Designator"] not in aircraft_categories[row["WTC"]]:
                aircraft_categories[row["WTC"]].append(row["Type Designator"])

for category in sorted(aircraft_categories):
    print(f"{category}: {len(aircraft_categories[category])}")
    
print ("Stranged categories:")
print(strangers)

print(sorted(aircraft_categories["H"]))