import glob

from check.check_defect import Defect
import time

from img_process.basic import read_image
from img_process.cut_image import save_img
from img_process.pre_process import get_useful_range
from utils import clear, get_image_name_from_path

if __name__ == '__main__':
    clear('temp/img')
    clear('temp/cut')
    # imgs = glob.glob('F:/Coding/python/graduation_design_image_process/image/*.tiff')
    imgs = glob.glob('F:/XMU/smartdsp/切割异常/数据集/NG/*.tiff')
    for img in imgs:
        # defect = Defect(img)
        # defect.cut_image()
        # res = defect.predict_cutted_images()
        # print(img.split('/')[-1], res)
        img_data = read_image(img)
        img_range = get_useful_range(img_data)
        save_img(img_data, img_range, f'temp/img/{get_image_name_from_path(img)}.png')
