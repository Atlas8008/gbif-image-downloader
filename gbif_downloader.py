import os
import json
import argparse

from utils.extract import extract, extract_multimedia_species_based
from utils.request_handler import GBIFRequestHandler, GLOBAL_DOWNLOAD_HANDLER


get_fname = lambda s: os.path.splitext(os.path.split(args.list_file)[1])[0]

def write_dois(dois):
    os.makedirs("dois/", exist_ok=True)

    doi_fname = os.path.splitext(
        os.path.split(args.list_file)[1]
    )[0] + "_doi.txt"

    with open("dois/" + doi_fname, "w") as f:
        f.write("\n".join(dois))

parser = argparse.ArgumentParser(description="Sets up downloads for species and download the observation data from the GBIF platform.")

parser.add_argument("list_file", type=str, help="The file containing the list of species to search and download.")
parser.add_argument("--extract", action="store_true", help="Flag; if set, the relevant files will be extracted to 'datasets/<species_name>'.")
parser.add_argument("--doi", action="store_true", help="Flag; if set, the DOIs of the downloads will be extracted and be written to doi/<list_file>_doi.txt.")
parser.add_argument("--basis_of_record", type=str, choices=("HUMAN_OBSERVATION", "PRESERVED_SPECIMEN"), default="HUMAN_OBSERVATION", help="The GBIF basis of record for the occurrence data.")
parser.add_argument("--filters", type=str, nargs="*", default=None, help="Additional filters marked by 'key=property', separated by space.")
parser.add_argument("--species_separate_requests", action="store_true", help="Flag; if set, the species occurrence data will be extracted separately from GBIF instead of a single large request.")
parser.add_argument("--skip_download", action="store_true", help="Flag; if set, the actual download will be skipped and an existing occurrence package will be extracted.")

args = parser.parse_args()

with open("auth.json", "r") as f:
    auth_data = json.load(f)

with open(args.list_file) as f:
    lines = f.read().strip().split("\n")

species_names = [species_name.strip() for species_name in lines if species_name.strip()]

print("Filters:", args.filters)

if args.filters:
    filters = {a: b for a, b in map(lambda s: s.split("=", 1), args.filters)}
else:
    filters = None


if args.species_separate_requests:
    handlers = []

    for species_name in species_names:
        handler = GBIFRequestHandler(
            species_name,
            basis_of_record=args.basis_of_record,
            filters=filters
        )
        handlers.append(handler)

        if not args.skip_download:
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

    if not args.skip_download:
        print("Waiting for inactivity...")

        GLOBAL_DOWNLOAD_HANDLER.wait_for_inactivity()

        if args.doi:
            print("Extracting DOIs...")

            dois = []

            for handler in handlers:
                dois.append("https://doi.org/" + handler.get_doi())

            write_dois(dois)

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
else:
    handler = GBIFRequestHandler(
        species_names,
        basis_of_record=args.basis_of_record,
        filters=filters
    )

    if not args.skip_download:
        ok = handler.generate_download_link(
            auth_data["user"],
            auth_data["password"],
            auth_data["email"],
        )

        actual_species_names = handler.actual_species_names

        if ok:
            processing_key = handler.queue_download(overwrite_original_name=True, download_name=get_fname(args.list_file))
            handler.wait_for_download(processing_key)
        else:
            print("Something went wrong during the download request")

        print("Waiting for inactivity...")

        GLOBAL_DOWNLOAD_HANDLER.wait_for_inactivity()

        if args.doi:
            print("Extracting DOI...")

            write_dois(["https://doi.org/" + handler.get_doi()])
    else:
        actual_species_names = {s: handler.get_actual_species_name(s) for s in species_names}

    if args.extract:
        print("Starting extraction...")

        zipfilepath = "downloads/" + get_fname(args.list_file) + ".zip"
        #target_path = "datasets/" + species_name

        extract_multimedia_species_based(
            zipfilepath=zipfilepath,
            species_names=[actual_species_names[s] for s in species_names],
            target_folders=["datasets/" + species_name for species_name in species_names]
        )

        print("Done.")

print("All done.")
