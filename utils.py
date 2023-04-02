import os
import shutil
from multiprocessing import cpu_count

CPU_COUNT = cpu_count()


def clear(dir):
    """
    if the path doesn't exist, it'll create, or it'll delete all the files
    :param dir:
    :return:
    """
    try:
        if not os.path.exists(dir):
            os.makedirs(dir)
        else:
            shutil.rmtree(dir)
            os.makedirs(dir)
        return True
    except:
        return False


def get_image_name_from_path(path: str):
    """
    get the name of the file from the path
    :param path:
    :return:
    """
    return path.split('\\')[-1].split('/')[-1].split('.')[0]
