import flet as ft
from flet_core import Theme

from ui.cutting_error_app import CuttingErrorApp


# Initialize the app
def ui(page: ft.Page):
    page.title = '液晶屏切割缺陷检测系统'
    page.window_width, page.window_height = 1000, 600  # 设置窗口初始化尺寸 set the initial size of the window
    page.window_min_width, page.window_min_height = 700, 400  # 设置窗口最小可调整尺寸 set the minimum size of the window
    # page.bgcolor = ft.colors.PINK
    cutting_error_app = CuttingErrorApp(page)  # 初始化要显示的内容 initialize the content to be shown

    def page_resize(e):
        """
        listen to event when the window size is changed
        :param e: event
        :return: None
        """
        size = page.window_width, page.window_height  # 获得当前窗口尺寸 get the current window size
        cutting_error_app.set_size(size)  # 对目标对象传入改变后的窗口尺寸大小 set the size to the target object

    page.on_resize = page_resize  # 设置窗口尺寸大小变化时的监听事件 set the event when the window size is changed
    page.overlay.append(cutting_error_app.pick_files_dialog)  # 选择文件对话框 set the file picker dialog
    page.fonts = {
        'OPPOSans': 'source/OPPOSans-M.ttf'
    }
    page.theme = Theme(font_family="OPPOSans")
    page.add(
        cutting_error_app
    )
    # print(page.platform)


def show():
    ft.app(target=ui)
