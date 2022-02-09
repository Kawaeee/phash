# -*- coding: utf-8 -*-
# phash.py :: Image deduplication using perceptual hashing

import argparse
import glob

import imagehash
from PIL import Image
from tqdm import tqdm
from icecream import ic

EXTENSION = [".png", ".jpg"]


def main(opt, hash_function=imagehash.phash):
    """
    main: Image de-duplication using Perceptual Hashing

    Argument:
    input_directory :: str - Input folder that we want to find duplicated images
    output_file :: str - A text file that contains duplicated images list

    Example:
    input_directory :: /home/test_path/
    output_file :: duplicated_filelist.txt
    """

    input_directory, output_file, verbose = opt.input_directory, opt.output_file, opt.verbose

    if verbose is False:
        ic.disable()

    list_of_images = []
    image_map = {}

    for ext in EXTENSION:
        for item in glob.glob(f"{input_directory}**/*{ext}", recursive=True):
            list_of_images.append(item)

    list_of_images.sort()

    for image_path in tqdm(list_of_images, desc="Loading Image: "):
        try:
            image = Image.open(image_path)
            hashed_image = hash_function(image)
        except Exception as e:
            print(e)
            continue

        image_map[hashed_image] = image_map.get(hashed_image, []) + [image_path]

    with open(output_file, "w") as duplicated_filelist:
        for image_hashed_value, image_list in image_map.items():
            image_count = len(image_list)
            image_pair_str = f"{image_count} :: {image_hashed_value} :: {image_list}"
            ic(image_pair_str)

            if image_count > 1:
                image_list.pop(0)
                for duplicated_image_path in image_list:
                    duplicated_filelist.writelines(f"{duplicated_image_path.strip()}\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--input-directory", type=str, default="input/", help="Input directory")
    parser.add_argument("-o", "--output-file", type=str, default="output.txt", help="Output file")
    parser.add_argument("-v", "--verbose", action="store_true", help="Enable verbosity")

    args = parser.parse_args()
    main(args)
