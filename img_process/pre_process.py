import time

import numpy as np
import cv2
import glob

from utils import clear

# img_path = 'image/1207 (2).tiff'
threshold = 150
threshold1 = 220
threshold2 = 150
threshold3 = 0.5
OUTPUT_PATH = 'output/imgs2'


def read_image(img_path: str) -> np.ndarray:
    """
    :param img_path:
    :return:
    """
    # not use imread api directly, because it can't open the path with Chinese character
    img = cv2.imdecode(np.fromfile(img_path, dtype=np.uint8), cv2.IMREAD_COLOR)
    return img


def image_binarization(img_data: np.ndarray) -> np.ndarray:
    # 将图片转为灰度图
    gray = cv2.cvtColor(img_data, cv2.COLOR_BGR2GRAY)

    # retval, dst = cv2.threshold(gray, 110, 255, cv2.THRESH_BINARY)
    # 最大类间方差法(大津算法)，thresh会被忽略，自动计算一个阈值
    retval, dst = cv2.threshold(gray, 65, 255, cv2.THRESH_BINARY)
    return dst


def get_useful_range(img_data: np.ndarray) -> tuple[int, int, int, int]:
    """
      c1      c2
    r1 +------+
       |      |
       |      |
       |      |
    r2 +------+
    :param img_data:
    :return:
    """
    r0, c0, _ = img_data.shape  # get the origin row and column
    r1, r2 = 0, r0 - 1
    c1, c2 = 0, c0 - 1

    # flatten_data = np.max(img_data, axis=2)  # flatten(r, g, b), just 1 channel left
    # flatten_data_by_col = np.max(flatten_data, axis=0).flatten()  # make each column flatten, just one row left
    # flatten_data_by_row = np.max(flatten_data, axis=1).flatten()  # make each row flatten, just one column left

    # for i in range(r0):
    #     if flatten_data_by_row[i] > threshold:
    #         r1 = i
    #         break
    # for i in range(r0 - 1, -1, -1):
    #     if flatten_data_by_row[i] > threshold:
    #         r2 = i
    #         break
    # for i in range(c0):
    #     if flatten_data_by_col[i] > threshold:
    #         c1 = i
    #         break
    # for i in range(c0 - 1, -1, -1):
    #     if flatten_data_by_col[i] > threshold:
    #         c2 = i
    #         break

    # for i in range(r0):
    #     if np.sum(flatten_data[i, :] > threshold1) > 300:
    #         r1 = i
    #         break
    # for i in range(r0 - 1, -1, -1):
    #     if np.sum(flatten_data[i, :] > threshold1) > 300:
    #         r2 = i
    #         break
    # for i in range(c0):
    #     if np.sum(flatten_data[:, i] > threshold2) > r0 / 30:
    #         c1 = i
    #         break
    # for i in range(c0 - 1, -1, -1):
    #     if np.sum(flatten_data[:, i] > threshold2) > r0 / 30:
    #         c2 = i
    #         break
    # print((r2-r1) * (c2-c1))
    dst = image_binarization(img_data)

    every_col_count = np.sum(dst == 255, axis=0)
    longest_col = np.max(every_col_count)
    every_row_count = np.sum(dst == 255, axis=1)
    longest_row = np.max(every_row_count)
    for i in range(r0):
        if every_row_count[i] > longest_row * threshold3:
            r1 = i
            break
    for i in range(r0 - 1, -1, -1):
        if every_row_count[i] > longest_row * threshold3:
            r2 = i
            break
    for i in range(c0):
        if every_col_count[i] > longest_col * threshold3:
            c1 = i
            break
    for i in range(c0 - 1, -1, -1):
        if every_col_count[i] > longest_col * threshold3:
            c2 = i
            break
    return r1, r2, c1, c2


def save_new_image(img_data: np.ndarray, new_range: tuple[int, int, int, int], new_path: str, fun=None):
    r1, r2, c1, c2 = map(int, new_range)
    new = img_data[r1: r2, c1: c2]
    if fun is not None:
        if not fun(new):
            return
    cv2.imwrite(new_path, new)


if __name__ == '__main__':
    imgs = glob.glob('image/*.tiff')
    clear(OUTPUT_PATH)
    print('clear')
    for img in imgs:
        t1 = time.time()
        name = img.split('\\')[-1].split('.')[0]
        img_data = read_image(img)
        new_range = get_useful_range(img_data)
        t2 = time.time()
        print(t2 - t1)
        save_new_image(img_data, new_range, f'{OUTPUT_PATH}/{name.replace(" ", "")}.bmp')
        print(time.time() - t2)
        print(f'{name} done!')
