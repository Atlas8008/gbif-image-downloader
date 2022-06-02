import os
import random
import argparse


random.seed(1338)

parser = argparse.ArgumentParser(description="This tool generates a subselection of items from a multimedia.txt provided a folder.")

parser.add_argument("folder", type=str, help="The folder for which to subselect the multimedia.")
parser.add_argument("count", type=int, help="The number of items to select.")

args = parser.parse_args()


with open(os.path.join(args.folder, "multimedia.txt"), "r") as f:
    lines = f.read().strip().split("\n")

# Skip header line as it's irrelevant
header = lines[0]
lines = lines[1:]

# Keep only lines that have an image file located at the fourth position
lines = [line for line in lines if line.split("\t")[3]]

random.shuffle(lines)

# Subselect
lines = lines[:args.count]

# Add header again and save
lines = [header] + lines

with open(os.path.join(
    args.folder, "multimedia_subset" + str(args.count) + ".txt"), "w") as f:
    f.write("\n".join(lines))