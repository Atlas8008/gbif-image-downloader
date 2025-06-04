# Description

This tools downloads images from GBIF observation data, e.g. for a selection of certain species, and bundles them into a single dataset that can be used for training machine learning algorithms.

# Prerequisites

## Installation
This tool only requires a working installation of python 3 (and the packages described in requirements.txt) and an account from [GBIF](http://gbif.org).

    pip install -r requirements.txt

## Setup

1. Before running the script, the API access data has to be set up. For this, copy the `auth_template.json` file to `auth.json` and replace the placeholders in the file with the actual account data, i.e., user name, password and e-mail.
2. Generate a dataset file. To do this, take as example the file `dataset_lists/example_ds.txt`. I.e., fill an empty file with lines containing species names or similar, which can be found on [GBIF](http://gbif.org). Each line corresponds to a single key (e.g., species) to be searched for in the database.
3. That's it, you're good to go!

## Script Calls
### Main Script

The main script for downloading the dataset can be called in the following way (with placeholders replaced):

    python download_dataset.py \
        <DATASET_FILE> \
        <N_IMAGES_PER_KEY> \
        --basis_of_record {HUMAN_OBSERVATION|PRESERVED_SPECIMEN}

This will download the entire dataset and put it into a new subfolder under './datasets/<DATASET_NAME>'. The tool will first request an occurrence dataset corresponding to your query and will occasionally check and wait until the dataset is ready. This process can take up to three hours. Afterwards, the required metadata will be extracted and the images be downloaded.

Be aware that the download of the complete dataset can take quite a while (estimate about 2 seconds per single image). By default, the images will be put into a single folder with all their meta information and a split script, which can be used to split the dataset in a training and validation part, if required. For more information on how to use that script, call the `create_train_val_split.py` script with the `--help` argument.

### Species Lookup

The `species_lookup.py` script can be used beforehand to check, which species or keys are found in the GBIF database with a certain dataset file, to catch wrong matches beforehand. It can be used simply like

    python species_lookup.py <DATASET_FILE>

### Other scripts

The remaining scripts (`download_media.py`, `extract_subset.py`, `gbif_downloader.py`) are usually called by the main script, but can also be called individually for more specific uses. To get more infos on these scripts, run the scripts with the `--help` argument.


# Citations

If you use any of the downloaded data in a publication, please cite the dataset according to the [GBIF Citation Guidelines](https://www.gbif.org/citation-guidelines).

For later reference, you can find the DOI(s) of the download in the [dois/](dois/) folder in a file corresponding to your dataset name, or also in the newly created dataset folder.