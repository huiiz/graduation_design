import glob

from check.check_defect import Defect
import time

from utils import clear

if __name__ == '__main__':
    clear('temp/img')
    clear('temp/cut')
    # imgs = glob.glob('F:/Coding/python/graduation_design_image_process/image/*.tiff')
    imgs = glob.glob('F:/XMU/smartdsp/切割异常/数据集/OK/*.tiff')
    for img in imgs:
        defect = Defect(img)
        defect.cut_image()
        res = defect.predict_cutted_images()
        print(img.split('/')[-1], res)
