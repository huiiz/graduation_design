import os
import shutil
from multiprocessing import cpu_count
from concurrent.futures import ThreadPoolExecutor, wait, ALL_COMPLETED

CPU_COUNT = cpu_count()


def clear(dir):
    """
    清除文件夹下的内容 if the path doesn't exist, it'll create, or it'll delete all the files
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
    从路径获取文件名称 get the name of the file from the path
    :param path:
    :return:
    """
    return path.split('\\')[-1].split('/')[-1].split('.')[0]


def speed_up(func, iter_ls, *args):
    """
    加速循环调用一个函数的运算，函数要求func(i, *args)
    :param func: 调用函数
    :param iter_ls: 循环的数据，列表
    :param args: 其他参数
    :return:
    """
    with ThreadPoolExecutor(max_workers=CPU_COUNT) as pool:
        all_task = [pool.submit(func, i, *args) for i in iter_ls]
        wait(all_task, return_when=ALL_COMPLETED)
