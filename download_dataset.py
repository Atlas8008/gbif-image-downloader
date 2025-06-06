import os
import argparse
import subprocess


parser = argparse.ArgumentParser(description="Sets up GBIF downloads for a provided set of species, creates an image subselection and downloads the selected images.")

parser.add_argument("dataset_file", type=str, help="The path to the file containing the species (one item per line).")
parser.add_argument("subset_size", type=str, help="The number of images to select and download.")
parser.add_argument("--no_pack", action="store_true", help="Flag; if set, the downloaded folders will not be put into a joint dataset folder with all metadata and necessary tools.")
parser.add_argument("--basis_of_record", type=str, choices=("HUMAN_OBSERVATION", "PRESERVED_SPECIMEN"), default="HUMAN_OBSERVATION", help="The GBIF basis of record for the occurrence data.")
parser.add_argument("--filters", type=str, nargs="*", default="", help="Additional filters marked by 'key=property', separated by space.")
parser.add_argument("--skip_download", action="store_true", help="Flag; if set, the actual download will be skipped and an existing occurrence package will be extracted.")
parser.add_argument("--download_images_only", action="store_true", help="Flag; if set, only images in the already prepared final folder structure will be downloaded and everything before will be skipped.")

args = parser.parse_args()



# Parse dataset list file
with open(args.dataset_file, "r") as f:
    item_names = f.read().strip().split("\n")

# Remove stuff like empty lines
item_names = [item for item in item_names if item]


if not args.download_images_only:
    print("Setting up and downloading occurrence and metadata...")

    if args.filters:
        filters = ["--filters", " ".join(args.filters)]
    else:
        filters = []

    additional_params = []

    if args.skip_download:
        additional_params.append("--skip_download")

    # Generate download links and download all the metadata
    if subprocess.call(
            ["python", "gbif_downloader.py", args.dataset_file, "--extract", "--doi", "--basis_of_record", args.basis_of_record] + filters + additional_params
        ):
        exit()

    print("Generating subsets...")

    for folder_name in item_names:
        # Extract the subsets
        if subprocess.call(
                ["python", "extract_subset.py", os.path.join('datasets/', folder_name), args.subset_size]
            ):
            exit()

print("Downloading images...")

# Download images for each folder
for folder_name in item_names:
    media_source_name = os.path.join(
        "datasets/",
        folder_name,
        "multimedia_subset" + str(args.subset_size) + '.txt'
    )

    # Extract the subsets
    if subprocess.call(
            ["python", "download_media.py", media_source_name]
        ):
        exit()

if not args.no_pack:
    import shutil

    print("Packing everything together...")

    dataset_name = os.path.splitext(os.path.split(args.dataset_file)[1])[0]

    dataset_path = os.path.join("datasets", dataset_name)

    os.makedirs(dataset_path)

    # Move all the image folders
    for folder_name in item_names:
        folder_path = os.path.join("datasets", folder_name)

        shutil.move(folder_path, dataset_path)

    # Copy doi-data
    shutil.copy(
        os.path.join("dois", dataset_name + "_doi.txt"),
        dataset_path,
    )

    # Copy tools
    tool_folder = "dataset_tools"

    for fname in os.listdir(tool_folder):
        tool_path = os.path.join(tool_folder, fname)

        shutil.copy(
            tool_path,
            dataset_path,
        )

    print("Done.")
