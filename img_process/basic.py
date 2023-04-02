import cv2
import numpy as np


def read_image(img_path: str) -> np.ndarray:
    """
    :param img_path:
    :return:
    """
    # not use imread api directly, because it can't open the path with Chinese character
    img = cv2.imdecode(np.fromfile(img_path, dtype=np.uint8), cv2.IMREAD_COLOR)
    return img


def get_image_by_range(img_data: np.ndarray, r1: int, r2: int, c1: int, c2: int) -> np.ndarray:
    """
    :param img_data:
    :param r1:
    :param r2:
    :param c1:
    :param c2:
    :return:
    """
    return img_data[r1:r2 + 1, c1:c2 + 1, :]