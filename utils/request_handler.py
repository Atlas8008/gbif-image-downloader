import os
import json
import time
import random
import requests
import threading

from utils.utils import search_match


class DownloadHandler:
    def __init__(self) -> None:
        self.queue = []
        self.handler_thread = None
        self.active = False

        self._downloads_processing = set()

    def enqueue(self, fn, *args, **kwargs):
        processing_key = self._get_processing_key()

        self._downloads_processing.add(processing_key)

        self.queue.append((processing_key, fn, args, kwargs))

        return processing_key

    def start(self):
        self.handler_thread = threading.Thread(target=self._handle_downloads, daemon=True)
        self.handler_thread.start()

    def _get_processing_key(self):
        key = None

        while key is None or key in self._downloads_processing:
            key = random.randint(0, 2 ** 64)

        return key

    def _handle_downloads(self):
        while True:
            if len(self.queue) > 0:
                self.active = True

                processing_key, fn, args, kwargs = self.queue.pop(0)

                print("Download Handler now processing:", fn, args, kwargs)

                try:
                    fn(*args, **kwargs)
                finally:
                    self._downloads_processing.discard(processing_key)
            else:
                self.active = False

                time.sleep(1)

    def wait_for_inactivity(self):
        time.sleep(1.5)

        while self.active:
            time.sleep(1)

    def wait_for_download(self, processing_key):
        print("Waiting for download for key", processing_key)
        while processing_key in self._downloads_processing:
            time.sleep(1)
        print("Finished waiting.")


class GBIFRequestHandler:
    def __init__(self, species_name, basis_of_record="HUMAN_OBSERVATION", filters=None, api_url="https://api.gbif.org/v1") -> None:
        self.species_name = species_name
        self.actual_species_names = None
        self.api_url = api_url
        self.basis_of_record = basis_of_record

        self.download_url = None
        self.wait_for_availability = False

        self.key = None

        if filters is None:
            filters = {}

        self.filters = filters

    def get_actual_species_name(self, species_name=None):
        if species_name is None:
            species_name = self.species_name

        response = requests.get(
            self.api_url + "/species/match",
            params={"name": species_name, "verbose": True}
        )

        response = json.loads(response.content)

        name = search_match(response)

        return name

    def get_doi(self, key=None):
        if key is None:
            key = self.key

        print("Getting doi from", self.api_url + "/occurrence/download/" + key)

        doi = None

        while doi is None:
            try:
                response = json.loads(requests.get(
                    self.api_url + "/occurrence/download/" + key,
                ).content)

                doi = response["doi"]
            except KeyError:
                print("DOI still missing, trying again in 10 seconds")
                time.sleep(10)

        return doi

    def generate_download_link(self, username, password, email):
        if not isinstance(self.species_name, list):
            species_names = [self.species_name]
            single_name = True
        else:
            species_names = self.species_name
            single_name = False

        actual_species_names = []
        orig_to_actual_dict = {}

        for species_name in species_names:
            print("Searching species name for", species_name)
            actual_species_name = self.get_actual_species_name(species_name)

            if actual_species_name == "":
                print("Did not find name for", species_name, ", Skipping...")
                if single_name: # Species not found
                    return False
            else:
                print("Found name", actual_species_name)

                actual_species_names.append(actual_species_name)
                orig_to_actual_dict[species_name] = actual_species_name

        self.actual_species_names = orig_to_actual_dict

        additional_filters = [
            {
                "type": "equals",
                "key": k.upper(),
                "value": v.upper(),
            } for k, v in self.filters.items()
        ]

        predicate = {
            "creator": username,
            "notificationAddresses": [
                email
            ],
            "sendNotification": True,
            "format": "DWCA",
            "predicate": {
                "type": "and",
                "predicates": [{
                    "type": "equals",
                    "key": "BASIS_OF_RECORD",
                    "value": self.basis_of_record.upper(),
                },{
                    "type": "equals",
                    "key": "MEDIA_TYPE",
                    "value": "StillImage"
                },{
                    "type": "or",
                    "predicates": [{
                        "type": "equals",
                        "key": "SCIENTIFIC_NAME",
                        "value": actual_species_name,
                    } for actual_species_name in actual_species_names]
                }] + additional_filters
            }
        }

        print("Generating download link for", ", ".join(species_names))

        response = requests.post(
            self.api_url + "/occurrence/download/request",
            data=json.dumps(predicate),
            auth=(username, password),
            headers={"Content-Type": "application/json"}
        )
        key = response.content.decode("utf-8")

        if not key.endswith(".zip"):
            key_fname = key + ".zip"
        else:
            key_fname = key

        self.download_url = self.api_url + "/occurrence/download/request/" + key_fname
        self.wait_for_availability = True

        print("Request finished, Status code:", response.status_code, ", Key: ", key)

        self.key = key

        return response.status_code in (200, 201)

    def queue_download(self, *args, **kwargs):
        processing_key = GLOBAL_DOWNLOAD_HANDLER.enqueue(self._download, *args, **kwargs)

        return processing_key

    def _download(self, *, download_url=None, overwrite_original_name=False, wait_for_availability=None, download_name=None):
        if download_url is not None:
            self.download_url = download_url

        print("Starting download routine for", self.download_url)

        fname = os.path.split(self.download_url)[1]

        if download_name is not None:
            fname = download_name + os.path.splitext(fname)[1]
        else:
            if overwrite_original_name:
                fname = self.species_name + os.path.splitext(fname)[1]
            else:
                fname = self.species_name + "_" + fname

        if wait_for_availability is None:
            wait_for_availability = self.wait_for_availability

        print("Trying to download from", self.download_url)
        if wait_for_availability:
            status_code = None

            while status_code != 200:
                download = requests.get(self.download_url)

                status_code = download.status_code

                print("Received status code", status_code, "for download from", self.download_url)

                if status_code != 200:
                    time.sleep(10)
        else:
            download = requests.get(self.download_url)

            print("Received status code", download.status_code, "for download from", self.download_url)

        print("Downloading", self.download_url)

        os.makedirs("downloads/", exist_ok=True)

        with open(os.path.join("downloads/", fname), "wb") as f:
            f.write(download.content)

        print("Finished downloading", self.download_url, "and wrote to file", os.path.join("downloads/", fname))

    def wait_for_download(self, processing_key):
        GLOBAL_DOWNLOAD_HANDLER.wait_for_download(processing_key)


GLOBAL_DOWNLOAD_HANDLER = DownloadHandler()
GLOBAL_DOWNLOAD_HANDLER.start()