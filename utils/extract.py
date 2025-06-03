import os
import io
import zipfile
import pandas as pd


def extract(zipfilepath, filepath, target_folder):
    os.makedirs(target_folder, exist_ok=True)

    if not isinstance(filepath, (list, tuple)):
        filepaths = [filepath]
    else:
        filepaths = filepath

    with zipfile.ZipFile(zipfilepath) as z:
        for filepath in filepaths:
            filename = os.path.split(filepath)[1]

            with open(os.path.join(target_folder, filename), "wb") as f:
                f.write(z.read(filepath))


def extract_multimedia_species_based(zipfilepath, species_names, target_folders):
    assert len(target_folders) == len(species_names), "The number of species names and target folders needs to be equal."

    with zipfile.ZipFile(zipfilepath) as z:
        print("Start Read")

        #occurrence_data = z.read("occurrence.txt")
        #multimedia_data = z.read("multimedia.txt")

        print("Start CSV")
        with z.open("occurrence.txt") as f:
            df_occ = pd.read_csv(f, delimiter="\t", dtype=str, usecols=["scientificName", "gbifID"], on_bad_lines="warn")
        print("Start Multimedia")
        with z.open("multimedia.txt") as f:
            df_mm = pd.read_csv(f, delimiter="\t", dtype=str, on_bad_lines="warn")
        # df_occ = pd.read_csv(io.BytesIO(occurrence_data), delimiter="\t", dtype=str, usecols=["scientificName", "gbifID"], low_memory=True)
        # df_mm = pd.read_csv(io.BytesIO(multimedia_data), delimiter="\t", dtype=str, low_memory=True)

        for species_name, target_folder in zip(species_names, target_folders):
            os.makedirs(target_folder, exist_ok=True)

            species_selection = df_occ[df_occ["scientificName"] == species_name]
            multimedia_lines = df_mm[df_mm["gbifID"].isin(species_selection["gbifID"])]

            multimedia_lines.to_csv(os.path.join(target_folder, "multimedia.txt"), sep="\t", index=False)