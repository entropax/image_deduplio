<h1> Deduplicator images. (cropeed include) </h1>

>*Преа́мбула: в связи со спецификой условий выполнения задачи, код далее написан исходя из  следующих принципов:*
>   - *Больше, не значит лучше.*
>   - *Сначала функционал, потом оптимизация.*
>   - Исходя из постановленной задачи, реализован дополнительный функционал<br>
>
>*Автор репозитория будет рад всей критике в части, например, оптимизации кода.*

<br>
<h2>Table of content</h2>

[_TOC_]

## Description ##
### The code is written according to the task by [ФГУП «ГРЧЦ»](https://grfc.ru/grfc/)
**Поставленная задача:**
<br>
*Необходимо реализовать дедупликацию изображений с кропом. Сформировать коллекцию из 30 произвольных изображений.
Среди 30 изображений должны быть, 2 одинаковых изображения (например поезда) и 3 одинаковых изображения (например животные) с кропом (т.е. по разному обрезанных).
С использованием готовых библиотек python необходимо реализовать дедупликацию изображений – т.е. определение копий, запрос на подтверждение и удаление из коллекции.*

**Aditional tasks (my self thoughts):**
* make automate process of create images collection for testing
* add TUI interface
* add simple GUI interface
* add multiprocessing support
* add mmap support for large files
* write test


## Install ##
* clone this repo `git clone https://github.com/entropax/image_deduplio`
* create virtual env `python3 -m venv ./.venv`
* run new venv `source .venv/bin/activate`
* update pip `python3 -m pip install --user --upgrade pip`
* install requirements `pip install -r requirements.txt`

Or just copy and paste this to your terminal, all_in_one command style:
```shell
git clone https://github.com/entropax/image_deduplio && \
python3 -m venv ./.venv && source .venv/bin/activate && \
python3 -m pip install --user --upgrade pip && pip install -r requirements.txt`
```
## Usage ##
enter `python3 image_deduplio/deduplio.py -h' for help
<!-- > You can also make chmod +x and add to your patch

## for fine cropped image (pattern find)
* openCv with match find TM_CCOEFF_NORMED, after grey sczling
 [exem](http://www.learningaboutelectronics.com/Articles/How-to-match-an-image-embedded-in-another-image-Python-OpenCV.php)
 [deta](https://docs.opencv.org/4.x/df/dfb/group__imgproc__object.html#ga3a7850640f1fe1f58fe91a2d7583695d)
* [Brute-Force Matching with SIFT](https://docs.opencv.org/3.4/dc/dc3/tutorial_py_matcher.html)
* using PIL PIXEL BY PIXEL aftergreyscaling
* using p-hash and hamming with pixel by pixel
## for equal image
* p-hash with hamming distance [soue](https://pypi.org/project/ImageHash/)
* average hash?
* https://pypi.org/project/SSIM-PIL/
* piLoow with hash and hammin [ex](https://stackoverflow.com/questions/71514124/find-near-duplicate-and-faked-images)
* тупо по хешу
* по пикселям
* Average hashing (AHash)

### Особенности реализации ###
-->
---------------
#### Note: ####
На взгляд автора хотелось бы уточнения в следующих вопросах:
> * Как выполнен crop:<br>
с замещенем белым (сохранением размера, crop fit white)?<br>
c растягиваием изображения до исходного разрешения (fit crop)?
> * формат изображений:<br>
  jpg, png, svg?
> * что значит одинаковые:<br>
  визуально для человека (визуальная идентичность, вроде расстояния Хемминга)?<br>
  одинаковые цветовые пиксели (побитное машинное совпадение)?<br>
  являются ли перевернутые изображения одинаковыми?<br>
