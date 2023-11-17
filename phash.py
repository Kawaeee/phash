# -*- coding: utf-8 -*-
# phash.py :: Image deduplication using perceptual hashing

import argparse
import glob
import os

import imagehash
import magic
import pyheif
from PIL import Image, ImageFile, UnidentifiedImageError
from tqdm import tqdm
from icecream import ic

ImageFile.LOAD_TRUNCATED_IMAGES = True

MIME_TYPES = ["image/png", "image/jpeg", "image/heic", "image/heif"]


def is_image_file(file_path):
    mime = magic.Magic(mime=True)
    file_mime = mime.from_file(file_path)
    return any(file_mime.startswith(mime_type) for mime_type in MIME_TYPES)


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

    for root, dirs, files in os.walk(input_directory):
        for file in files:
            file_path = os.path.join(root, file)
            if is_image_file(file_path):
                list_of_images.append(file_path)
    list_of_images.sort()

    for image_path in tqdm(list_of_images, desc="Loading Image: "):
        try:
            image = Image.open(image_path)
            hashed_image = hash_function(image)
        except UnidentifiedImageError:
            try:
                heif_file = pyheif.read(image_path)
                image = Image.frombytes(
                    heif_file.mode,
                    heif_file.size,
                    heif_file.data,
                    "raw",
                    heif_file.mode,
                    heif_file.stride,
                )
                hashed_image = hash_function(image)
            except Exception as other_exception:
                print(other_exception)
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
