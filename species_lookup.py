import json
import argparse
import requests

parser = argparse.ArgumentParser(description="Sets up downloads for species and download the observation data from the GBIF platform.")

parser.add_argument("list_file", type=str, help="The file containing the list of species to look up.")

args = parser.parse_args()

with open(args.list_file, "r") as f:
    species_names = f.read().strip().split("\n")

for species_name in species_names:
    print("Looking up species", species_name, "...")

    response = requests.get(
        "https://api.gbif.org/v1/species/match",
        params={"name": species_name}
    )

    response = json.loads(response.content)

    print("Found:", response["scientificName"])
    print()