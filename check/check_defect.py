import glob
import os.path
import time

import numpy as np
from PIL import Image
from matplotlib import pyplot as plt

from img_process.cut_image import cut_0, save_img
from img_process.new_process import line_cut
from utils import CPU_COUNT, clear

from img_process.pre_process import get_useful_range
from img_process.basic import read_image, get_image_by_range
from network.predict import Predict
from concurrent.futures import ThreadPoolExecutor

predict = Predict()
pool = ThreadPoolExecutor(max_workers=CPU_COUNT)
CUT_PATH = 'temp/cut'


class Defect:
    def __init__(self, img_path: str):
        self.useful_range = None
        self.processed_image_data = None
        self.cut_i = None
        self.cut_j = None
        if not os.path.exists(img_path):
            raise FileNotFoundError('image path not found')
        self.path = img_path
        self.name = img_path.split('\\')[-1].split('/')[-1].split('.')[0]
        self.img_data = read_image(self.path)
        self.cut_path = f'{CUT_PATH}/{self.name}'
        clear(self.cut_path)

    def cut_image(self):
        """
        cut the processed image into picecs and save them into a folder named by filename
        :return:
        """
        useful_range = get_useful_range(self.img_data)
        save_img(self.img_data, useful_range, f'temp/img/{self.name}.png')
        cuts = line_cut(self.img_data)
        for cut_range in cuts:
            save_img(self.img_data, cut_range, f'{self.cut_path}/{cut_range[0]}_{cut_range[2]}.png')

    def predict_cutted_images(self):
        images = glob.glob(f'{self.cut_path}/*.png')
        # result_map = np.ones((self.cut_i, self.cut_j))
        ng_dt = dict()
        for image in images:
            [i, j] = image.split('\\')[-1].split('.')[0].split('_')
            # print(i, j, end=' ')
            # pool.submit(self.predict_single_img, image, result_map, int(i), int(j))
            res, cls, prob = predict.to_predict(image)
            if res == 0 and prob > 0.7:
                img = read_image(image)
                max_ps = np.max(img, axis=2)
                percentage = np.sum(max_ps > 80) / max_ps.size
                # print(percentage, end=' ')
                if percentage > 0.1:
                    ng_dt[f'{i}_{j}'] = prob.item()
            # print(cls, prob)

            # result_map[int(i), int(j)] = res
            # print(i, j, res)
            # img = Image.open(image)
            # plt.title(f'{i}, {j}, {res}')
            # plt.imshow(img)
            # plt.show()
        # pool.shutdown()
        # print(np.min(result_map))

        # print(result_map)
        return ng_dt

    # def predict_single_img(self, image, result_map, i, j):
    #     res = predict.to_predict(image)
    #     result_map[int(i), int(j)] = res


if __name__ == '__main__':
    defect = Defect('')
