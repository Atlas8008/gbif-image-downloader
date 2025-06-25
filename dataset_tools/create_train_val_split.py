import os
import json
import random
import argparse


parser = argparse.ArgumentParser(description=
                                    "This script split the images in the " +
                                    "dataset subfolders into training and" +
                                    "validation sets and saves them to a " +
                                    "json file.")

parser.add_argument("train_size", type=int, help=
                                    "The number of images of each class " +
                                    "in the training set.")
parser.add_argument("--val_size", type=int, default=None, help=
                                    "The number of images of each class " +
                                    "in the validation set. If not set, " +
                                    "all images not contained in the " +
                                    "training set will be used.")

args = parser.parse_args()

random.seed(1339)
target_filename = "data.json"

folders = [d for d in os.listdir(".") if os.path.isdir(d)]

folders = sorted(folders)

data_dict = {
    "train": {},
    "val": {},
}

for folder in folders:
    image_files = [fname for fname in os.listdir(folder) if fname.endswith(".jpg")]

    image_files = sorted(image_files)

    random.shuffle(image_files)

    train_image_files = image_files[:args.train_size]
    if args.val_size is None:
        val_image_files = image_files[args.train_size:]
    else:
        val_image_files = image_files[args.train_size:args.train_size + args.val_size]

    data_dict["train"][os.path.basename(folder)] = train_image_files
    data_dict["val"][os.path.basename(folder)] = val_image_files

    print("Class:", folder)
    print(f"\ttrain: {len(train_image_files)}, val: {len(val_image_files)}")

# Save everything
with open(target_filename, "w") as f:
    f.write(json.dumps(data_dict))

# Save folder names as class names
with open("class_names.txt", "w") as f:
    f.write("\n".join(folders))

