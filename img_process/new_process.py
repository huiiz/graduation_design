import json

import numpy as np

from img_process.cut_image import save_img, cut_0

from img_process.pre_process import get_useful_range, read_image

STEP = 128
SIZE = 512
PATH = 'new_output/cut'


def get_main_column_index(c0, c1, c2):
    c_index = 1 if c1 > (c0 - c2) else 2
    return c_index


def line_cut(image_data):
    r0, c0, _ = image_data.shape
    r1, r2, c1, c2 = get_useful_range(image_data)
    c_index = get_main_column_index(c0, c1, c2)

    # line_a, row1; line_b, row2
    r_a = int(max(0, r1 - SIZE / 2))
    r_b = int(r_a + SIZE)
    r_d = int(min(r0, r2 + SIZE / 2))
    r_c = int(r_d - SIZE)
    c_a = int(max(0, c1 - SIZE / 2))
    c_b = int(c_a + SIZE)
    while c_a < c2 and c_b < c0:
        # to_path1 = f'{output_path}/{name.split(".")[0].replace(" ", "_")}_{r_a}_{c_a}.jpg'
        yield r_a, r_b, c_a, c_b

        # to_path2 = f'{output_path}/{name.split(".")[0].replace(" ", "_")}_{r_c}_{c_a}.jpg'
        yield r_c, r_d, c_a, c_b
        c_a += STEP
        c_b += STEP

    #line_c, column
    r_e = int(max(0, r1 - SIZE / 2))
    r_f = int(r_e + SIZE)
    if c_index == 1:
        c_c = int(max(0, c1 - SIZE / 2))
        c_d = int(c_c + SIZE)
    else:
        c_d = int(min(c0, c2 + SIZE / 2))
        c_c = int(c_d - SIZE)
    while r_e < r2 and r_f < r0:
        # to_path3 = f'{output_path}/{name.split(".")[0].replace(" ", "_")}_{r_e}_{c_c}.jpg'
        # print(r_e, r_f, c_c, c_d)
        yield r_e, r_f, c_c, c_d
        r_e += STEP
        r_f += STEP


if __name__ == '__main__':
    import glob
    from utils import clear
    clear(PATH+'/ng')
    clear(PATH+'/ok')
    clear('new_output/img')
    imgs = glob.glob('image\\*')
    # imgs = glob.glob('image\\1207-3_(16)*')
    # imgs = ['image\\1207-3_(7).tiff', 'image\\1212_(11).tiff', 'image\\1220_(2).tiff']
    for img in imgs:
        name = img.split('\\')[-1].split('.')[0]
        with open(f'new_output/label/{name}.json') as f:
            ranges = json.load(f)
        image_data = read_image(img)
        # test
        ran = get_useful_range(image_data)
        save_img(image_data, ran, f'new_output/img/{name}.png')
        # test
        cuts = line_cut(image_data)
        for cut_range in cuts:
            cut_0(image_data, cut_range, ranges, name)
        print(f'{name} finish!')