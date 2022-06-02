import os
import zipfile


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
