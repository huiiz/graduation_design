import cv2
import numpy as np
from PIL import Image


def read_image(img_path: str) -> np.ndarray:
    """
    :param img_path:
    :return:
    """
    # not use imread api directly, because it can't open the path with Chinese character
    img = cv2.imdecode(np.fromfile(img_path, dtype=np.uint8), cv2.IMREAD_COLOR)
    return img


def get_image_by_range(img_data: np.ndarray, ranges: tuple[int, int, int, int]) -> np.ndarray:
    """
    :param img_data:
    :param ranges:
    :return:
    """
    r1, r2, c1, c2 = ranges
    return img_data[r1:r2 + 1, c1:c2 + 1, :]


def get_img_size(img_path):
    img = Image.open(img_path)
    return img.size
