#! /bin/python
"""
image_deduplio - Python package for finding duplicate or similar images
"""

import os
import shutil
import time
import argparse
from random import choice, sample
import itertools
from subprocess import call

import cv2 as cv
from PIL import Image
from imagehash import phash
import requests
from tqdm import tqdm
from tkinter import Tk, filedialog


# parse CLI arguments
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
        self.generate_test_amount = generate_test_amount

    def select_folder(self):
        root = Tk()
        root.withdraw()
        return filedialog.askdirectory()

    def download_image(self, path, search_term, resolution, postfix):
        response = requests.get(
                f"https://source.unsplash.com/random/{resolution}/?"
                + str(search_term) + ", allow_redirects=True")
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
                        path + os.path.splitext(img_name)[0] + '_CROPPED.jpg')

    def generate_random_collection(
            self,
            images_dir='./test_images/',
            amount=30):
        os.makedirs(images_dir, exist_ok=True)
        categories = ['train', 'kitty', 'programming', 'space']
        resolutions = ['small', 'medium', 'large', 'original']
        for number in tqdm(range(1, amount+1)):
            self.download_image(
                    images_dir,
                    choice(categories),
                    choice(resolutions),
                    number
                    )
        print('\n***generate some fake duplicates images***')
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
        except Exception as e:
            return e

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
        '''Ask user to delete one duplication file.'''
        answer = ''
        delete_counter = 0
        if not files:
            return
        for img_1_path, img_2_path in files:
            if answer == 'q':
                break
            answer = ''
            img_1 = Image.open(img_1_path)
            img_2 = Image.open(img_2_path)
            while answer not in ['1', '2', 'c', 'q']:
                print(
                    'Duplicate files:\n',
                    f'File 1 {os.path.basename(img_1_path)} with resolution',
                    f'{img_1.size[0]}x{img_1.size[1]}\n',
                    f'File 2 {os.path.basename(img_2_path)} with resolution',
                    f'{img_2.size[0]}x{img_2.size[1]}\n\n',
                    'Type "1" or "2" for deleting File 1/File 2\n',
                    'Type "c" to continue\n',
                    'Type "q" to exit\n',
                    )
                answer = input('Enter here: ')
                if answer == '1':
                    try:
                        os.remove(img_1_path)
                        for name in files:
                            if img_1_path in name:
                                files.remove(name)
                        delete_counter += 1
                        print(f'\nFile {img_1_path} was DELETE\n')
                    except FileNotFoundError:
                        print('File not found')
                if answer == '2':
                    try:
                        os.remove(img_2_path)
                        for name in files:
                            if img_1_path in name:
                                files.remove(name)
                        delete_counter += 1
                        print(f'\nFile {img_2_path} was DELETE\n')
                    except FileNotFoundError:
                        print('File not found')
                if answer == 'c':
                    call('clear' if os.name == 'posix' else 'cls')
                if answer == 'q':
                    call('clear' if os.name == 'posix' else 'cls')
                    break
        print(f'\nCongratulations! you delete {delete_counter} files!')
        print('Thanks for using this program.\nBye dear user!')

    def run(self):
        start = time.time()
        if self.gui_folder_pick:
            self.path = self.select_folder() + '/'
        if self.generate_test_amount:
            self.generate_random_collection(amount=self.generate_test_amount)
            print('\nCollection created! Check ./test_images/ folder')
            return 0
        if not os.path.isdir(self.path):
            print('Path is not valid! Try with -p PATH argument, or add "/"')
            return 0
        print(f'Check duplicates in *{self.path}* folder')
        try:
            dup_images, dup_cropped_images = self.find_duplicate(self.path)
            print(f'\nElapsed time: {time.time() - start:.0f} seconds, hurray!')
            duplicate_amount = len(dup_images) + len(dup_cropped_images)
            print(f'\n{duplicate_amount} duplicate files founded!\n')
            if not duplicate_amount:
                print('You dont have any duplicate, it is amazing!')
                return 0
            self.delete_request(dup_images + dup_cropped_images)
        except FileNotFoundError:
            print('Path is not valid! Try with -p PATH argument, or add "/"')


if __name__ == '__main__':
    args = parser_cli()
    app = DeduplioApp(
            path=args.path,
            gui_folder_pick=args.gui,
            generate_test_amount=args.gen_amount)
    app.run()
