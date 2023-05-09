import os.path

import numpy as np

from img_process.new_process import line_cut
from utils import CPU_COUNT, get_image_name_from_path, speed_up

from img_process.basic import read_image, get_image_by_range
from network.predict import Predict
from concurrent.futures import ThreadPoolExecutor

predict = Predict()
pool = ThreadPoolExecutor(max_workers=CPU_COUNT)
CUT_PATH = 'temp/cut'

cut_dt = {}
defect_imgs_dt = {}


def get_cut_dt(key: str):
    return cut_dt[key]


def set_cut_dt(key: str, value: list):
    cut_dt[key] = value
    return cut_dt


def clear_cut_dt():
    cut_dt = {}
    return cut_dt


def get_defect_imgs_dt(name: str, place: str=None):
    if place is None:
        return defect_imgs_dt[name]
    return defect_imgs_dt[name][place]


def set_defect_imgs_dt(name: str, place: str, value: np.ndarray):
    defect_imgs_dt.setdefault(name, {})
    defect_imgs_dt[name][place] = value
    return defect_imgs_dt


def clear_defect_imgs_dt():
    defect_imgs_dt = {}
    return defect_imgs_dt


class Defect:
    def __init__(self, img_path: str):
        self.useful_range = None
        self.processed_image_data = None
        self.cut_i = None
        self.cut_j = None
        if not os.path.exists(img_path):
            raise FileNotFoundError('image path not found')
        self.path = img_path
        self.name = get_image_name_from_path(img_path)
        self.img_data = read_image(self.path)
        # self.cut_path = f'{CUT_PATH}/{self.name}'
        # clear(self.cut_path)

    def cut_image(self):
        """
        cut the processed image into picecs and save them into a folder named by filename
        :return:
        """
        # useful_range = get_useful_range(self.img_data)
        # save_img(self.img_data, useful_range, f'temp/img/{self.name}.png')
        cuts = line_cut(self.img_data)
        points = [cut for cut in cuts]
        set_cut_dt(self.name, points)
        # for cut_range in points:
        #     save_img(self.img_data, cut_range, f'{self.cut_path}/{cut_range[0]}_{cut_range[2]}.png')



    def predict_cutted_images(self):
        """
        预测这张大图中所有小图的结果
        :return:
        """
        points = get_cut_dt(self.name)
        # images = glob.glob(f'{self.cut_path}/*.png')
        # result_map = np.ones((self.cut_i, self.cut_j))
        ng_dt = dict()
        # for image in images:
        def predict_img(point_tuple: tuple, ng_dt: dict):
            i, _1, j, _2 = point_tuple
            # print(i, j, end=' ')
            # pool.submit(self.predict_single_img, image, result_map, int(i), int(j))
            img_data = get_image_by_range(self.img_data, point_tuple)
            res, cls, prob = predict.to_predict(img_data)
            if res == 0 and prob > 0.7:
                max_ps = np.max(img_data, axis=2)
                percentage = np.sum(max_ps > 80) / max_ps.size
                # print(percentage, end=' ')
                if percentage > 0.05:
                    ng_dt[f'{i}_{j}'] = prob.item()
                    set_defect_imgs_dt(self.name, f'{i}_{j}', img_data)
        # 加速测试
        # import time
        # t1 = time.time()
        # for point_tuple in points:
        #     predict_img(point_tuple, ng_dt)
        # print(f'未加速耗时{time.time()-t1}秒')
        # t1 = time.time()
        speed_up(predict_img, points, ng_dt)
        # print(f'加速后耗时{time.time()-t1}秒')

        return ng_dt

    # def predict_single_img(self, image, result_map, i, j):
    #     res = predict.to_predict(image)
    #     result_map[int(i), int(j)] = res


if __name__ == '__main__':
    defect = Defect('')
