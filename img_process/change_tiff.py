import base64
import numpy as np
import cv2


def change_tiff_into_thumb(img_path: str, new_size: int = 100) -> np.ndarray | None:
    """
    将大尺寸tiff格式图片转化为小尺寸缩略图
    :param img_path: 要调整的图片尺寸
    :param new_size: 要调整的图片大小
    :return: 调整后的缩略图
    """
    if not img_path:
        return None
    # 不直接使用imread接口，这是因为无法打开中文路径
    img = cv2.imdecode(np.fromfile(img_path, dtype=np.uint8), cv2.IMREAD_COLOR)
    height, width, _ = img.shape
    if height > width:
        h1 = (height - width) // 2
        h2 = (height + width) // 2 - 1
        w1 = 0
        w2 = width - 1
    else:
        h1 = 0
        h2 = height - 1
        w1 = (width - height) // 2
        w2 = (width + height) // 2 + 1
    cutted_image = img[h1: h2, w1: w2]
    resized_img = cv2.resize(cutted_image, (new_size, new_size))
    return resized_img


def cv2_base64(image: np.ndarray) -> str | None:
    """
    将cv2图片转为base64格式
    :param image: np.ndarray格式图片数据
    :return: base64格式图片
    """
    if type(image) != np.ndarray:
        return None
    base64_str = cv2.imencode('.jpg', image)[1].tostring()
    base64_str = base64.b64encode(base64_str)
    base64_str = str(base64_str)[2:-1]
    return base64_str
