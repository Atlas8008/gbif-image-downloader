from concurrent.futures import thread
import os
import json
import time
import requests
import threading


class DownloadHandler:
    def __init__(self) -> None:
        self.queue = []
        self.handler_thread = None
        self.active = False
        
    def enqueue(self, fn, *args, **kwargs):
        self.queue.append((fn, args, kwargs))
        
    def start(self):
        self.handler_thread = threading.Thread(target=self._handle_downloads, daemon=True)
        self.handler_thread.start()
    
    def _handle_downloads(self):
        while True:
            if len(self.queue) > 0:
                self.active = True
                
                fn, args, kwargs = self.queue.pop(0)
                
                print("Download Handler now processing:", fn, args, kwargs)
                
                fn(*args, **kwargs)
            else:
                self.active = False
                
                time.sleep(1)
    
    def wait_for_inactivity(self):
        time.sleep(1.5)
        
        while self.active:
            time.sleep(1)
            

class GBIFRequestHandler:
    def __init__(self, species_name, api_url="https://api.gbif.org/v1") -> None:
        self.species_name = species_name
        self.api_url = api_url
        
        self.download_url = None
        self.wait_for_availability = False
        
    def generate_download_link(self, username, password, email):
        print("Generating download link for", self.species_name)
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
                    "value": "HUMAN_OBSERVATION"
                },{
                    "type": "equals",
                    "key": "MEDIA_TYPE",
                    "value": "StillImage"
                },{
                    "type": "like",
                    "key": "SCIENTIFIC_NAME",
                    "value": self.species_name + "*"
                }]
            }
        }
        
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
        
        return response.status_code in (200, 201)
        
    def queue_download(self, *args, **kwargs):
        GLOBAL_DOWNLOAD_HANDLER.enqueue(self._download, *args, **kwargs)        

    def _download(self, *, download_url=None, overwrite_original_name=False, wait_for_availability=None):
        if download_url is not None:
            self.download_url = download_url
            
        print("Starting download routine for", self.download_url)
        
        fname = os.path.split(self.download_url)[1]
        
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
        
        with open(os.path.join("downloads/", fname), "wb") as f:
            f.write(download.content)
        
        print("Finished downloading", self.download_url, "and wrote to file", os.path.join("downloads/", fname))
            

GLOBAL_DOWNLOAD_HANDLER = DownloadHandler()
GLOBAL_DOWNLOAD_HANDLER.start()