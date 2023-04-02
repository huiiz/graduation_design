import numpy as np

from img_process.pre_process import read_image, save_new_image
import glob
import json
from utils import clear

# NEW_WIDTH = 256
# NEW_HEIGHT = 256
NEW_WIDTH = 512
NEW_HEIGHT = 512
STEP = 128
THRESHOLD = 128
OK_PATH = 'output/cut2/OK'
NG_PATH = 'output/cut2/NG'
# OK_PATH = 'new_output/cut/ok'
# NG_PATH = 'new_output/cut/ng'
OK_PATH1 = 'output/ok_cut'



def cut(img_data: np.ndarray, name: str, ranges: list):
    r, c, _ = img_data.shape
    r0, c0 = 0, 0
    i = 0
    while not r0 == r:
        r1, r2, c1, c2, r0, c0 = get_range(r0, c0, r, c)
        new_range = r1, r2, c1, c2
        cut_0(img_data, new_range, ranges, name)
        i += 1


def cut_0(img_data, new_range, ranges, name):
    r1, r2, c1, c2 = new_range
    for ran in ranges:
        if is_overlap(new_range, tuple(ran)):
            path = f'{NG_PATH}/{name.split(".")[0].replace(" ", "_")}_{r1}_{c1}.jpg'
            save_img(img_data, new_range, path)
            break
    else:
        path = f'{OK_PATH}/{name.split(".")[0].replace(" ", "_")}_{r1}_{c1}.jpg'
        save_img(img_data, new_range, path)


def cut_1(img_data: np.ndarray, name: str):
    r, c, _ = img_data.shape
    r0, c0 = 0, 0
    i = 0
    while not r0 == r:
        r1, r2, c1, c2, r0, c0 = get_range(r0, c0, r, c)
        new_range = r1, r2, c1, c2
        save_img(img_data, new_range, f'{OK_PATH1}/{name}_{r1}_{c1}.jpg')
        i += 1


def is_overlap(range1: tuple[int, int, int, int], range2: tuple[int, int, int, int]):
    """
    To check if two rectangles are overlying
    :param range1:
    :param range2:
    :return:
    """
    abs_y = abs((range1[0] + range1[1]) / 2 - (range2[0] + range2[1]) / 2)
    abs_x = abs((range1[2] + range1[3]) / 2 - (range2[2] + range2[3]) / 2)
    if abs_y < (range1[1] - range1[0] + range2[1] - range2[0]) / 2 and abs_x < (
            range1[3] - range1[2] + range2[3] - range2[2]) / 2:
        return True
    return False


# def is_in(p: tuple[int, int], rectangle: tuple[int, int, int, int]):
#     """
#     to check if one point is inside a rectangle
#     :param p:
#     :param rectangle:
#     :return:
#     """
#     r0, c0 = p
#     r1, r2, c1, c2 = rectangle
#     return r1 <= r0 <= r2 and c1 <= c0 <= c2


def get_range(r0, c0, r, c):
    if c0 == c:
        # need to go to next row
        c1, c2 = 0, min(c, NEW_WIDTH)
        r1, r2 = max(min(r0 + STEP + NEW_HEIGHT, r) - NEW_HEIGHT, 0), min(r0 + STEP + NEW_HEIGHT, r)
        r0 = min(r0 + STEP, r)
        c0 = min(STEP, c)
    else:
        c1, c2 = max(min(c0 + NEW_WIDTH, c) - NEW_WIDTH, 0), min(c0 + NEW_WIDTH, c)
        r1, r2 = max(min(r0 + NEW_HEIGHT, r) - NEW_HEIGHT, 0), min(r0 + NEW_HEIGHT, r)
        c0 = c0 + STEP if c2 < c else c
    # print(r1, r2, c1, c2, r0, c0)
    return r1, r2, c1, c2, r0, c0


def save_img(img_data: np.ndarray, new_range: tuple[int, int, int, int], new_path: str):
    def check(new: np.ndarray):
        # print(new.tolist())
        if np.max(new) < THRESHOLD:
            return False
        else:
            return True


    save_new_image(img_data, new_range, new_path, check)



if __name__ == '__main__':
    # imgs = glob.glob('output/imgs2/*.bmp')
    imgs = glob.glob('image/*.tiff')
    clear(OK_PATH)
    clear(NG_PATH)
    print('success to clear')
    for img in imgs:
        img_data = read_image(img)
        name = img.split('\\')[-1].split('.')[0]
        with open(f'new_output/label/{name}.json') as f:
            ranges = json.load(f)

        cut(img_data, name, ranges)
        print(f'{name} done!')
