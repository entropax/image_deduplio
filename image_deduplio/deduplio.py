#! /bin/python
"""
image_deduplio - Python script for finding duplicate and similar images
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
            Find duplicated and cropped images and
            providing delete duplicates
            ''')
    parser.add_argument(
            '-p',
            '--path',
            help='specify directory contain collection of images',
            nargs='?',
            const='./test_images/',
            default='.',
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
        self.path = os.path.normpath(path)
        self.gui_folder_pick = gui_folder_pick
        self.generate_test_amount = generate_test_amount

    def select_folder(self):
        root = Tk()
        root.withdraw()
        return filedialog.askdirectory()

    def download_image(self, path, search_term, resolution, postfix):
        try:
            response = requests.get(
                f'https://source.unsplash.com/random/{resolution}/?'
                + str(search_term) + ', allow_redirects=True')
            response.raise_for_status()
        except requests.RequestException as error:
            print(error)
        with open(f'{path}{search_term}_{postfix}.jpg','wb') as img:
                img.write(response.content)
        return f'Saved to: {path}{search_term}_{postfix}.jpg'

    def generate_fake_duplicates(self, path, amount):
        img_files = list(filter(lambda x: 'jpg' in x, os.listdir(path)))
        for img_name in sample(img_files, amount):
            source = path + img_name
            dest = path + os.path.splitext(img_name)[0] + '_DUPLICATE.jpg'
            print(f'duplicate: {img_name} with _DUPLICATE preffix')
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
                print(f'crop and save: {img_name} with _CROPPED preffix')
                cropped_image.save(
                        path + os.path.splitext(img_name)[0] + '_CROPPED.jpg')

    def generate_random_collection(
            self,
            images_dir='./test_images/',
            amount=30):
        if amount == None:
            return 0
        if amount <= 0:
            print('Input not zero or negative amount!')
            exit()
        os.makedirs(images_dir, exist_ok=True)
        downloaded = []
        categories = ['train', 'kitty', 'programming', 'space']
        resolutions = ['small', 'medium', 'large', 'original']
        print('Loading images')
        for number in tqdm(range(1, amount+1), position=0, leave=True):
            downloaded.append(self.download_image(
                    images_dir,
                    choice(categories),
                    choice(resolutions),
                    number
                    ))
        print(*downloaded, sep='\n')
        print('\n***generated some fake duplicates images in collection***')
        self.generate_fake_duplicates(images_dir, amount=1)
        print('\n***generated some randomly cropped images in collection***')
        self.random_crop_images(images_dir, amount=3)
        print('\nCollection created! Check ./test_images/ folder')
        answer = input(f'Do you want scan "{images_dir}*" type "y"/"n": ')
        self.path = os.path.normpath(images_dir)
        if answer != 'y':
            exit()

    def is_image_duplicate(self, img1_path, img2_path, hamming_distance=3):
        with Image.open(img1_path) as img1, Image.open(img2_path) as img2:
            img1_hash = phash(img1)
            img2_hash = phash(img2)
        if img1_hash - img2_hash < hamming_distance:
            return True

    def is_image_cropped(self, img_path, template_path):
        img = cv.imread(img_path, cv.IMREAD_GRAYSCALE)
        template = cv.imread(template_path, cv.IMREAD_GRAYSCALE)
        if img.shape == template.shape:
            return False
        try:
            result = cv.matchTemplate(img, template, cv.TM_CCOEFF_NORMED).max()
            if result >= 0.95:
                return True
        except Exception as e:
            return e

    def find_duplicate(self, path):
        print(f'Check duplicates in {self.path} folder')
        duplicated_images = []
        duplicated_cropped_images = []
        files = [os.path.normpath(path + '/' + file_name)
                for file_name in os.listdir(path)]
        img_files = list(filter(lambda x: '.jpg' in x, files))
        img_pairs = list(itertools.combinations(img_files, 2))
        for img_1_path, img_2_path in tqdm(img_pairs):
            if self.is_image_duplicate(img_1_path, img_2_path):
                duplicated_images.append((img_1_path, img_2_path))
                for pair in img_pairs:
                    if img_1_path in pair:
                        img_pairs.remove(pair)
            elif self.is_image_cropped(img_1_path, img_2_path):
                duplicated_cropped_images.append((img_1_path, img_2_path))
        dup_amount = len(duplicated_images) + len(duplicated_cropped_images)
        print(f'\n{dup_amount} duplicate files founded!')
        if not dup_amount:
            print(f'\n{dup_amount} duplicate files founded!\n')
            print('You dont have any duplicate, it is amazing!')
            exit()
        return (duplicated_images, duplicated_cropped_images)

    def term_ui(self, files):
        '''Ask user to delete one duplication file.'''
        to_deleted = ['',]
        for img1_path, img2_path in files:
            answer = ''
            with Image.open(img1_path) as img1, Image.open(img2_path) as img2:
                while answer not in ['1', '2', 'c', 'q', 'cls']:
                    print(
                        'Duplicate files:\n',
                        f'File_1 {os.path.basename(img1_path)} with resolution',
                        f'{img1.size[0]}x{img1.size[1]}\n',
                        f'File_2 {os.path.basename(img2_path)} with resolution',
                        f'{img2.size[0]}x{img2.size[1]}\n\n',
                        'Type "1" or "2" for mark File_1/File_2 to delete\n',
                        'Type "c" to continue\n',
                        'Type "cls" to clear screen\n',
                        'Type "q" to exit\n',
                        f'Duplicate files left {len(files)//2}:\n',
                        f'\nLast marks file {to_deleted[-1]}:\n',
                        )
                    answer = input('Enter here: ')
                    if answer == '1':
                        to_deleted.append(img1_path)
                        for pair in files:
                            if img1_path in pair:
                                files.remove(pair)
                    if answer == '2':
                        to_deleted.append(img2_path)
                        for pair in files:
                            if img1_path in pair:
                                files.remove(pair)
                    if answer == 'c':
                        call('clear' if os.name == 'posix' else 'cls')
                    if answer == 'cls':
                        answer = ''
                        call('clear' if os.name == 'posix' else 'cls')
                    if answer == 'q':
                        to_deleted = set(to_deleted)
                        to_deleted.remove('')
                        print('\n', *to_deleted, sep='\n')
                        answer = input('Do you want to delete this files y/n: ')
                        if answer == 'y':
                            for img in to_deleted:
                                os.remove(img)
                        print(f'\nNice! You deleted all marks files!')
                        print('Thanks for using this program.\nBye dear user!')
                        exit()
        to_deleted = set(to_deleted)
        to_deleted.remove('')
        print('\n', *to_deleted, sep='\n')
        for img in to_deleted:
            os.remove(img)
        print(f'\nCongratulations! you delete {len(to_deleted)} files!')
        print('Thanks for using this program.\nBye dear user!')

    def run(self):
        if self.gui_folder_pick:
            self.path = os.path.normpath(self.select_folder())
        self.generate_random_collection(amount=self.generate_test_amount)
        if not os.path.isdir(self.path):
            print('Path is not valid! Try with -p PATH argument, or add "/"')
            exit()
        try:
            start = time.time()
            dup_images, dup_cropped_images = self.find_duplicate(self.path)
            print(f'\nElapsed time: {time.time() - start:.0f} seconds, nice!\n')
            self.term_ui(dup_images + dup_cropped_images)
        except FileNotFoundError:
            print('Path is not valid! Try with -p PATH argument, or add "/"')


if __name__ == '__main__':
    args = parser_cli()
    app = DeduplioApp(
            path=args.path,
            gui_folder_pick=args.gui,
            generate_test_amount=args.gen_amount)
    app.run()
