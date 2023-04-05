from threading import Timer

import numpy as np

from check.check_defect import Defect, clear_cut_dt, clear_defect_imgs_dt
from log.log import logger
import flet as ft
from ui.result_body import ResultBody
from ui.result_panel import ResultPanel
from ui.image_item import ImageItem
from utils import get_image_name_from_path


# 程序主界面 the main window
class CuttingErrorApp(ft.UserControl):
    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        self.width, self.height = parent.width, parent.height  # 获取界面尺寸 get the size of the window
        self.init_data()
        # 顶部操作栏BEGIN
        self.pick_files_dialog = ft.FilePicker(on_result=self.select_images)  # 文件选择器 file picker
        self.top_bar = ft.Row(
            controls=[
                ft.ElevatedButton(text="批量选择要处理的图像文件",
                                  icon=ft.icons.IMAGE_SEARCH,  # 图标
                                  on_click=lambda _: self.pick_files_dialog.pick_files(
                                      allow_multiple=True,  # 是否允许多选
                                      allowed_extensions=[  # 允许的文件后缀名
                                          'jpg', 'png', 'tiff', 'webp', 'jfif', 'jpeg', 'bmp'
                                      ]
                                  )),
                ft.ElevatedButton("开始分析", icon=ft.icons.LINE_AXIS_ROUNDED, on_click=self.process),
            ],
            alignment=ft.MainAxisAlignment.CENTER
        )
        # 顶部操作栏END

        self.pb = ft.ProgressBar(visible=False)  # 进度条
        parent.snack_bar = ft.SnackBar(content=ft.Text(value=''))  # 提示框
        self.tip_box = parent.snack_bar

        # 中间内容BEGIN
        self.thumb_img_ls = ft.Column(  # 1.缩略图列表
            spacing=5,
            scroll=ft.ScrollMode.ALWAYS,  # 设置显示滚动栏

        )
        self.main_content = ResultBody(self)  # 2.中间显示图片目标检测内容

        self.result_panel = ResultPanel(self)  # 3.结果面板
        self.vertical_divider = ft.VerticalDivider(width=3)  # 垂直分隔符 vertical divider
        self.body = ft.Row(  # 中间内容合并   merge the middle content
            controls=[
                ft.Container(
                    content=self.thumb_img_ls,
                    expand=2,  # expand设置占用比例 set the proportion of the space
                    alignment=ft.alignment.top_center
                ),
                self.vertical_divider,
                ft.Container(
                    content=self.main_content,
                    expand=15,
                    alignment=ft.alignment.center
                ),
                self.vertical_divider,
                ft.Container(
                    content=self.result_panel,
                    expand=6,
                ),
            ],
            alignment=ft.MainAxisAlignment.START,  # 靠左对齐 align to the left
            spacing=0,
            # expand=True,
        )
        self.set_body_height()  # 设置缩略图显示列表 height
        self.update_thumbs()  # 更新缩略图显示 update the thumbnail list
        # 中间内容END

    def build(self):
        return ft.Column(
            controls=[
                self.top_bar,
                ft.Divider(height=1, thickness=0.6),
                self.body,
                self.pb,
            ],
        )

    def init_data(self):
        self.img_list = []  # 设置传入图像列表 set the list of images to be processed
        self.selected_image_item = None  # 被选中的图像 selected image
        self.defect_dt = {}  # 缺陷数据 defect data
        self.have_select = False  # 是否已经选择了图像
        self.begin_to_process = False  # 是否开始处理图像
        self.predict_result = {}  # 预测结果 predict result, True表示有缺陷，False表示无缺陷
        self.final_result = {}  # 最终结果 final result

    def set_body_height(self):
        """
        根据窗口大小，自适应设置缩略图列表的高度 according to the size of the window, set the height of the thumbnail list
        :return: None
        """
        self.body.height = self.height - 120  # 设置窗口内容大小，将窗口大小减去一个值

    def set_pb_value(self, value: float = 1.0):
        """
        设置进度条值 set the value of the progress bar
        :param value:
        :return:
        """
        if not self.pb.visible and value < 1:
            self.pb.visible = True
        self.pb.value = value
        self.pb.update()
        # 设置延迟消失BEGIN
        if value == 1:
            def set_hidden():
                self.pb.visible = False
                self.update()

            t = Timer(1, set_hidden)  # 延迟1s set delay to 1s
            t.start()
        # 设置延迟消失END

    def set_tip_value(self, value: str = ''):  # 设置提示框内容 set the content of the tip box
        self.tip_box.open = True
        self.tip_box.content = ft.Text(value=value)
        self.parent.update()

        # 设置延迟消失BEGIN
        def set_hidden():
            self.tip_box.open = False
            self.parent.update()

        t = Timer(0.7, set_hidden)  # 延迟1.5s set delay to 1.5s
        t.start()

    def set_size(self, size: tuple[float, float]):
        """
        调节窗口大小时，动态获得窗口尺寸 adjust the size of the window, dynamically get the size of the window
        :param size: 窗口尺寸，宽度和高度 window size, width and height
        :return: None
        """
        self.width, self.height = size  # 获得传入窗口大小
        self.set_body_height()
        self.update()

    def update_thumbs(self):
        """
        更新缩略图列表 update the thumbnail list
        :return: None
        """
        self.thumb_img_ls.controls.clear()  # 1.清除现有显示的缩略图内容 clear the existing thumbnail content
        to_insert_thumbs = []  # 2.确定需要插入的缩略图对象 list of thumbnails to be inserted
        img_len = len(self.img_list)
        success_count = 0
        for path in self.img_list:
            try:
                to_insert_thumbs.append(ImageItem(
                    img_path=path,
                    parent=self
                ))
                success_count += 1
                self.set_pb_value(success_count / img_len)
            except Exception as e:
                logger.error(f'CuttingErrorApp {path}传入出错\n{e}')
                img_len -= 1
        minimum_to_show_img_num = 1  # 最小要显示图片数量 minimum number of images to show
        if len(to_insert_thumbs) < minimum_to_show_img_num:
            to_insert_thumbs.extend(
                [ImageItem(
                    img_path='source\\to_show_img.png',
                    name='选择要处理图片',
                    parent=self
                ) for _ in range(minimum_to_show_img_num - len(to_insert_thumbs))]
            )
        self.thumb_img_ls.controls.extend(to_insert_thumbs)  # 3.插入待显示缩略图
        self.selected_image_item = None  # 4.将选中缩略图对象置为空
        self.begin_to_process = False  # 5.将开始处理标志置为False

    def select_images(self, e: ft.FilePickerResultEvent):
        """
        选择需要上传的图片 select the image to be uploaded
        :param e: 点击对象 click object
        :return: None
        """
        if not e.files:
            return None
        '''
        map(function,iterable,...)，即
        - 第一个参数为函数，这里使用了lambda表达式，表示要获取的文件路径； the first parameter is the function, here using the lambda expression, representing the file path to be obtained;
        - 第二个参数为可迭代的对象，这里的e.files表示了传入的文件 the second parameter is the iterable object, here the e.files represents the file passed in
        通过map映射获得了所有文件的文件名
        '''
        self.init_data()
        self.img_list = list(map(lambda f: f.path, e.files))
        self.have_select = True
        self.update_thumbs()  # 更新缩略图 update the thumbnail
        self.main_content.reset()
        self.result_panel.reset()
        self.update()

    def process(self, e):
        """
        处理图片 process the image
        :return: None
        """
        if not self.have_select:
            self.set_tip_value('请先选择图片')
            return
        if self.begin_to_process:
            if len(self.defect_dt) < len(self.img_list):
                self.set_tip_value('正在处理中，请耐心等待，不要重复点击')
                return
            self.set_tip_value('请先选择图片')
            return
        self.defect_dt = {}
        self.begin_to_process = True
        self.set_tip_value('分析数据中，请耐心等待......')
        clear_cut_dt()
        clear_defect_imgs_dt()
        i = 0
        for img in self.img_list:
            defect = Defect(img)
            i += 0.25
            self.set_pb_value(i / len(self.img_list))
            defect.cut_image()
            i += 0.25
            self.set_pb_value(i / len(self.img_list))
            name = get_image_name_from_path(img)
            self.defect_dt[name] = defect.predict_cutted_images()
            have_defect = len(self.defect_dt[name]) > 0 and max(self.defect_dt[name].values()) > 0.9
            self.predict_result[name] = have_defect
            self.final_result[name] = have_defect
            if i == 0.5:
                self.thumb_img_ls.controls[0].click()
            else:
                self.result_panel.update()
            i += 0.5
            self.set_pb_value(i / len(self.img_list))
            # print(img, 'finish', self.defect_dt[img])

        self.set_tip_value('分析结束')

        print(self.defect_dt)

