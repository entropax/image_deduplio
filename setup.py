from setuptools import setup
import os

base_dir = os.path.dirname(__file__)

with open(os.path.join(base_dir, "README.md")) as f:
    long_description = f.read()

setup(
  name = 'deduplio',
  packages = ['deduplio'],
  version = '0.8.0',
  license='SL',
  description = 'image_deduplio - Python script for finding duplicate and similar images.'
  long_description=long_description,
  long_description_content_type='text/markdown',
  author = 'Sol Maxwell',
  author_email = 'entropax@posteo.net',
  url = 'https://github.com/entropax/image_deduplio',
  download_url = 'https://github.com/entropax/image_deduplio/archive/refs/tags/v0.8.0.tar.gz',    # change everytime for each new release
  keywords = ['duplicate', 'image', 'finder', 'similarity', 'pictures', 'cropped'],
  install_requires=[
          'Pillow',
          'cv',
          'ImageHash',
          'opencv-python',
          'requests',
          'tqdm',
      ],
  classifiers=[
    'Development Status :: 4 - Alpha/Unstable',      # Chose either "3 - Alpha", "4 - Beta" or "5 - Production/Stable" as the current state of your package
    'Intended Audience :: Developers',
    'Topic :: Software Development :: Build Tools',
    'License :: OSI Approved :: SL License',
    'Programming Language :: Python :: 3.7',
    'Programming Language :: Python :: 3.8', #Specify which pyhton versions to support
    'Programming Language :: Python :: 3.9',
  ],
)
