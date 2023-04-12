import os
import json
import argparse

from utils.extract import extract
from utils.request_handler import GBIFRequestHandler, GLOBAL_DOWNLOAD_HANDLER

parser = argparse.ArgumentParser(description="Sets up downloads for species and download the observation data from the GBIF platform.")

parser.add_argument("list_file", type=str, help="The file containing the list of species to search and download.")
parser.add_argument("--extract", action="store_true", help="Flag; if set, the relevant files will be extracted to 'datasets/<species_name>'.")
parser.add_argument("--doi", action="store_true", help="Flag; if set, the DOIs of the downloads will be extracted and be written to doi/<list_file>_doi.txt.")
parser.add_argument("--basis_of_record", type=str, choices=("HUMAN_OBSERVATION", "PRESERVED_SPECIMEN"), default="HUMAN_OBSERVATION", help="The GBIF basis of record for the occurrence data.")

args = parser.parse_args()

with open("auth.json", "r") as f:
    auth_data = json.load(f)

with open(args.list_file) as f:
    lines = f.read().strip().split("\n")

species_names = [species_name.strip() for species_name in lines if species_name.strip()]

handlers = []

for species_name in species_names:
    handler = GBIFRequestHandler(species_name, basis_of_record=args.basis_of_record)
    handlers.append(handler)

    ok = handler.generate_download_link(
        auth_data["user"],
        auth_data["password"],
        auth_data["email"],
    )

    if ok:
        processing_key = handler.queue_download(overwrite_original_name=True)
        handler.wait_for_download(processing_key)
    else:
        print("Something went wrong for", species_name)

print("Waiting for inactivity...")

GLOBAL_DOWNLOAD_HANDLER.wait_for_inactivity()

if args.doi:
    print("Extracting DOIs...")

    os.makedirs("dois/", exist_ok=True)

    dois = []

    for handler in handlers:
        dois.append("https://doi.org/" + handler.get_doi())

    doi_fname = os.path.splitext(
        os.path.split(args.list_file)[1]
    )[0] + "_doi.txt"

    with open("dois/" + doi_fname, "w") as f:
        f.write("\n".join(dois))


if args.extract:
    print("Starting extraction...")
    for species_name in species_names:
        zipfilepath = "downloads/" + species_name + ".zip"
        target_path = "datasets/" + species_name

        print("Extracting", zipfilepath, "to", target_path, "...")

        extract(
            zipfilepath=zipfilepath,
            filepath=["multimedia.txt", "rights.txt"],
            target_folder=target_path,
        )

        print("Done.")

print("All done.")