#! /bin/python
"""
dedupex - Python package for finding duplicate or similar images within folders
https://github.com/elisemercury/Duplicate-Image-Finder
"""

import os
import shutil
import time
import argparse
import collections
from random import choice, sample
import itertools

import numpy as np
import cv2 as cv
from PIL import Image, ImageTk
from imagehash import phash
import requests
from tqdm import tqdm
from tkinter import Tk, filedialog

# set CLI arguments
def parser_cli():
    parser = argparse.ArgumentParser(
            prog='deduplio.py',
            description='''
            Find duplicated image and crop image parent,
            also provide delete duplicates
            ''')
    parser.add_argument(
            '-p',
            '--path',
            help='specify directory contain collection of images',
            nargs='?',
            const='./test_images/',
            dest='path',
            )
    parser.add_argument(
            '-gen',
            help='generate collection of images in ./test_images folder',
            nargs='?',
            const=30,
            type=int,
            dest='gen_amount',
            )
    parser.add_argument(
            '-gui',
            help='simple gui folder pick',
            action='store_true',
            )
    return parser.parse_args()


class DeduplioApp():
    def __init__(
            self,
            path='.',
            generate_test_amount=None,
            gui_folder_pick=False,
            ):
        self.path = path
        self.gui_folder_pick = gui_folder_pick
        self.generate_test_amount=generate_test_amount

    def select_folder(self):
        root = Tk()
        root.withdraw()
        return filedialog.askdirectory()


    def download_image(self, path, search_term, resolution, postfix):
        response = requests.get(
                f"https://source.unsplash.com/random/{resolution}/?"
                + str(search_term)+", allow_redirects=True")
        print(
                f"Download file and saving to: {path}"
                + str(search_term) + "_" + str(postfix) + ".jpg")
        open(
                f"{path}"
                + str(search_term) + "_"
                + str(postfix) + ".jpg", 'wb').write(response.content)

    def generate_fake_duplicates(self, path, amount):
        img_files = list(filter(lambda x: 'jpg' in x, os.listdir(path)))
        for img_name in sample(img_files, amount):
            source = path + img_name
            dest = path + os.path.splitext(img_name)[0] + '_DUPLICATE.jpg'
            print(f'duplicate: {img_name} with _DUPLICATE.jpg preffix')
            shutil.copyfile(source, dest)


    def random_crop_images(self, path, amount):
        img_files = list(filter(lambda x: 'jpg' in x, os.listdir(path)))
        for img_name in sample(img_files, amount):
            with Image.open(path + img_name) as img:
                width, height = img.size
                crop_box = (
                        choice(range(0, width//2+1)),
                        choice(range(0, height//2+1)),
                        choice(range(width, width//2-1, -1)),
                        choice(range(height, height//2-1, -1)),
                        )
                cropped_image = img.crop(crop_box)
                print(f'crop and save: {img_name} with _CROPPED.jpg preffix')
                cropped_image.save(
                        path + os.path.splitext(img_name)[0] +'_CROPPED.jpg')


    def generate_random_collection(
            self,
            images_dir='./test_images/',
            amount=30):
        os.makedirs(images_dir, exist_ok=True)
        categories = ['train', 'kitty', 'programming', 'space']
        resolutions = ['small', 'medium', 'large', 'original']
        for number in range(1, amount+1):
            self.download_image(
                    images_dir,
                    choice(categories),
                    choice(resolutions),
                    number
                    )
        print('\n***generate some fage duplicates images***')
        self.generate_fake_duplicates(images_dir, amount=1)
        print('\n***generate some randomly cropped images***')
        self.random_crop_images(images_dir, amount=3)


    def is_image_duplicate(self, img_path_1, img_path_2, hamming_distance=5):
        img_1 = Image.open(img_path_1)
        img_2 = Image.open(img_path_2)
        if phash(img_1) - phash(img_2) < hamming_distance:
            return True


    def is_image_cropped(self, img_path, template_path):
        img = cv.imread(img_path, cv.IMREAD_GRAYSCALE)
        template = cv.imread(template_path, cv.IMREAD_GRAYSCALE)
        if img.shape == template.shape:
            return False
        try:
            result = cv.matchTemplate(img, template, cv.TM_CCOEFF_NORMED).max()
            if result >= 0.75:
                return True
        except:
            return False


    def find_duplicate(self, path):
        duplicated_images = []
        duplicated_cropped_images = []
        files = [path + file_name for file_name in os.listdir(path)]
        img_files = list(filter(lambda x: '.jpg' in x, files))
        img_pairs = list(itertools.combinations(img_files, 2))
        # print(*img_files, sep='\n')
        for img_1, img_2 in tqdm(img_pairs):
            if self.is_image_duplicate(img_1, img_2):
                # print(img_1 + ' and ' + img_2 + " DULEP")
                duplicated_images.append((img_1, img_2))
                for pair in img_pairs:
                    if img_1 in pair:
                        img_pairs.remove(pair)
            elif self.is_image_cropped(img_1, img_2):
                # print(img_1 + ' and ' + img_2 + " CROPPED" )
                duplicated_cropped_images.append((img_1, img_2))
        return (duplicated_images, duplicated_cropped_images)


    def delete_request(self, files):
        for file_1, file_2 in files:
            print(files)

    def run(self):
        start = time.time()
        if self.generate_test_amount:
            self.generate_random_collection(amount=self.generate_test_amount)
            print('\nCollection created! Check ./test_images/ folder')
            return 0
        if self.gui_folder_pick:
            self.path = self.select_folder() + '/'
        print(f'Check duplicates in *{self.path}* folder')
        dup_images, dup_cropped_images = self.find_duplicate(self.path)
        print(f'\nElapsed time: {time.time() - start:.0f} seconds, hurray!')
        self.delete_request(dup_images)
        self.delete_request(dup_cropped_images)


if __name__ == '__main__':
    args = parser_cli()
    app = DeduplioApp(
            path=args.path,
            gui_folder_pick=args.gui,
            generate_test_amount=args.gen_amount,
            )
    app.run()
