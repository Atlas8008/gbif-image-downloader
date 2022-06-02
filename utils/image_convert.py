import io

from PIL import Image


def save_data_as_image(data, fname):
    img = Image.open(io.BytesIO(data))
    
    #print(img.format)
    img.save(fname)


if __name__ == "__main__":
    source_fname = "/home/mkoerschens/datasets/gbif_download_sets/gbif_ia_preserved/achillea millefolium/2.jpg"
    target_fname = "/home/mkoerschens/datasets/gbif_download_sets/gbif_ia_preserved/achillea millefolium/2_new.jpg"
    
    with open(source_fname, "rb") as f:
        save_data_as_image(f.read(), target_fname)
    
    import requests
    
    #data = requests.get("https://www.unimus.no/felles/bilder/web_hent_bilde.php?id=12109017&type=jpeg").content
    
    
    #save_data_as_jpg_image(data, target_fname)
    