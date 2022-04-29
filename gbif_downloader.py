import json

from request_handler import GBIFRequestHandler, GLOBAL_DOWNLOAD_HANDLER


with open("auth.json", "r") as f:
    auth_data = json.load(f)

species_name = "Acer pseudoplatanus"

handler = GBIFRequestHandler(species_name)

ok = handler.generate_download_link(
    auth_data["user"],
    auth_data["password"],
    auth_data["email"],
)

if ok:
    handler.queue_download()

#handler.queue_download(download_url="http://api.gbif.org/v1/occurrence/download/request/0062582-200221144449610.zip")

print("Waiting for inactivity...")

GLOBAL_DOWNLOAD_HANDLER.wait_for_inactivity()
