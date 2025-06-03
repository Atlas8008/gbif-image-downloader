import json
import argparse
import requests

from utils.utils import search_match

parser = argparse.ArgumentParser(description="Looks up a list of species names in the GBIF database to check what actual name or synonym would be found when searching for a specific term or name.")

parser.add_argument("list_file", type=str, help="The file containing the list of species to look up.")
parser.add_argument("--nomatch_only", action="store_true", help="Flag; if set, only the GBIF names will be printed that do not contain the query name.")

args = parser.parse_args()


with open(args.list_file, "r") as f:
    species_names = f.read().strip().split("\n")

for species_name in species_names:
    if not args.nomatch_only:
        print("Looking up species", species_name, "...")

    response = requests.get(
        "https://api.gbif.org/v1/species/match",
        params={"name": species_name, "verbose": True}
    )

    response = json.loads(response.content)

    species_match = search_match(response)

    try:
        if not args.nomatch_only or species_name not in species_match:
            if species_match == "":
                print("Found no match for", species_name, f"({response})")
            else:
                print("Found:", species_match, f"(instead of {species_name})")
            if not args.nomatch_only:
                print()
    except KeyError as e:
        print(f"Species {species_name}", str(e), response)
