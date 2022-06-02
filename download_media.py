import os
import time
import requests
import argparse

from utils.image_convert import save_data_as_image


parser = argparse.ArgumentParser(description="This tool generates a subselection of items from a multimedia.txt provided a folder.")

parser.add_argument("file", type=str, help="The multimedia table file for which to download media.")
parser.add_argument("--target_path", type=str, default=None, help="The target folder in which to put the downloaded files. By default, the folder of the provided multimedia file is used.")
parser.add_argument("--skip_existing", action="store_true", help="Flag; if set, will only try to download the images not already existing.")

args = parser.parse_args()

N_MAX_RETRIES = 5

if args.target_path:
    target_path = args.target_path
else:
    target_path = os.path.split(args.file)[0]

with open(args.file, "r") as f:
    lines = f.read().strip().split("\n")

# Skip header line as it's irrelevant
lines = lines[1:]

for i, line in enumerate(lines):
    fname = os.path.join(target_path, f"{i}.jpg")
    
    if args.skip_existing and os.path.exists(fname):
        print(fname, "already exists, skipping...")
        
        continue    
    
    items = line.split("\t")
    
    url = items[3]
    
    failure = False
    
    #with open(fname, "wb") as f:
    print("Downloading", url, "to", fname)
    
    retry_count = 0
    
    while True:
        try:
            response = requests.get(url, allow_redirects=True, timeout=10)
            
            response_status_code = response.status_code
            
            if response_status_code == 200:
                #f.write(response.content)
                save_data_as_image(response.content, fname)
                
                break
            
            retry_count += 1
                
            if retry_count < N_MAX_RETRIES:            
                print(f"Download failed (status {response_status_code}), retrying again in 5 seconds...")
                time.sleep(5)
            else:       
                print(f"Download failed (status {response_status_code}), skipping...")
            
                failure = True
                
                break
        except BaseException as e:
            print("Error during processing download:")
            print(e)
            
            print()
            print("Skipping...")
            
            failure = True
            
            break
            
    if failure and os.path.exists(fname):
        os.remove(fname)
        
    time.sleep(0.5)

print("Done.")