from threading import Timer

from log.log import logger
from img_process.change_tiff import cv2_base64, change_tiff_into_thumb, read_image
import flet as ft


# 图像缩略图中单个图像
class ImageItem(ft.UserControl):
    def __init__(self, img_path: str, name: str = None, parent=None):
        """
        初始化缩略图对象
        :param img_path: 传入图像本地地址
        :param name: 图像名称，可不填
        :param parent: 调用该组件的父对象
        """
        super().__init__()
        self.img_name = name if name else img_path.split('\\')[-1]  # 设置该缩略图对象的图像名字
        self.img_base64 = cv2_base64(
            image=change_tiff_into_thumb(img_path=img_path, new_size=200)  # 获得图像一定大小缩略图的编码为base64格式的数据
        )
        self.parent = parent  # 设置调用该对象的父类
        self.main_content = parent.main_content  # 获取父类对应显示
        self.selected = False  # 是否是被选中的（对颜色进行适当调整）
        # 图片部分
        self.img_content = ft.Image(
            src_base64=self.img_base64,
            fit=ft.ImageFit.CONTAIN,
        )
        # 文字显示部分
        self.text_container = ft.Container(
            content=ft.Text(
                value=self.img_name,
                color=ft.colors.BLACK,
                size=12,
                weight=ft.FontWeight.BOLD,
            ),
            alignment=ft.alignment.top_center,
            bgcolor=ft.colors.ORANGE_200,
            opacity=0.5,  # 初始透明的为0.5
        )

    def build(self):
        return ft.Container(
            content=ft.Stack(
                controls=[
                    self.img_content,
                    self.text_container,
                ],
            ),
            on_click=self.click,
            border=ft.border.all(width=1, color=ft.colors.BLACK38),
            # width=102,
            on_hover=self.on_hover,
        )

    def set_text_attr(self, attr: str, value: str | float):
        """
        设置文本对象的属性
        :param attr: 待设置属性
        :param value: 待设置属性值
        :return: None
        """
        match attr:
            case 'bgcolor':
                self.text_container.bgcolor = value
            case 'opacity':
                self.text_container.opacity = value
            case 'color':
                self.text_container.content.color = value

        self.text_container.update()

    def set_selected_status(self):
        """
        将本缩略图设置为选中状态
        :return: None
        """
        self.set_text_attr(attr='bgcolor', value=ft.colors.ORANGE_500)
        self.set_text_attr(attr='opacity', value=0.8)
        self.set_text_attr(attr='color', value=ft.colors.WHITE)

    def set_cancel_selected_status(self):
        """
        将本缩略图设置为取消选中状态
        :return: None
        """
        self.set_text_attr(attr='bgcolor', value=ft.colors.ORANGE_200)
        self.set_text_attr(attr='opacity', value=0.5)
        self.set_text_attr(attr='color', value=ft.colors.BLACK)

    def on_hover(self, e: ft.control_event.ControlEvent):
        """
        单个缩略图hover事件
        :param e: hover对象
        :return: None
        """
        # print(str(e))
        match e.data:
            case 'true':
                self.set_selected_status()
            case 'false':
                if not self.selected:
                    self.set_cancel_selected_status()

    def click(self, e: ft.control_event.ControlEvent):
        """
        单个缩略图点击事件
        :param e: 点击对象
        :return: None
        """
        if self.parent.selected_image_item:  # 如果调用父类中已经有选中的缩略图对象
            if id(self.parent.selected_image_item) == id(self):  # 判断选中的缩略图是不是当前这个
                return
            self.parent.selected_image_item.selected = False  # 取消原对象的选中状态
            self.parent.selected_image_item.set_cancel_selected_status()  # 将原对象样式调整为未选中状态
        self.selected = True  # 将当前对象设为选中状态
        self.parent.selected_image_item = self  # 将调用父类选中缩略图对象设置为本对象
        self.set_selected_status()  # 设置当前对象样式为选中状态
        self.main_content.content = ft.Text(  # 将结果传入 TODO：待修改
            f'点击了{self.img_name}'
        )
        self.main_content.update()


# 结果显示控制面板，包括裁决该图像是否为切割异常，以及导出与显示最终结果
class ResultPanel(ft.UserControl):
    def __init__(self, parent):
        """
        初始化结果控制面板
        :param parent:
        """
        super().__init__()
        self.item_name: str = ''  # 当前图像名字
        self.parent = parent

        # 单图部分BEGIN
        self.predict_percentage = ft.Text(  # 显示区块为切割异常的可能性
            value='本区域为切割异常的可能性为：94%'
        )
        self.predict_result = ft.Text(  # 显示当前图片文件预测是否为切割异常的结果
            value='预测结果为：有缺陷'
        )
        self.final_result = ft.Text(  # 显示当前图片文件最终是否为切割异常的结果
            value='最终结果为：有缺陷'
        )
        self.change_button = ft.ElevatedButton(  # 点击修改结果按钮
            text='预测结果错误，点击修改'
        )
        self.single_control_panel = ft.Column(
            controls=[
                self.predict_percentage,
                self.predict_result,
                self.change_button
            ],
            alignment=ft.MainAxisAlignment.CENTER
        )
        # 单图部分BEGIN

        # 所有图像部分BEGIN
        self.all_result = ft.Text(  # 整体数量部分
            value='本批共选中16张样品图像，其中4张为存在缺陷样品，12张为无缺陷样品'
        )
        self.show_result = ft.ElevatedButton(  # 预览结果
            text='预览结果',
            on_click=None
        )
        self.export_result = ft.ElevatedButton(  # 保存结果为文件
            text='保存结果',
            on_click=None
        )
        self.all_control_panel = ft.Column(
            controls=[
                self.all_result,
                self.show_result,
                self.export_result
            ],
            alignment=ft.MainAxisAlignment.CENTER
        )
        # 所有图像部分END

    def build(self):
        return ft.Column(
            controls=[
                ft.Container(
                    content=self.single_control_panel
                ),
                ft.Divider(),  # 水平分割线
                ft.Container(
                    content=self.all_control_panel
                ),
            ],
            alignment=ft.MainAxisAlignment.CENTER
        )

    def update(self):
        pass
        super().update()


# 结果主体内容
class ResultBody(ft.UserControl):
    def __init__(self, img_paths: list, parent):
        super().__init__()
        # 演示数据
        if not img_paths:
            img_paths = ['source/demo.png']
        self.parent = parent
        self.img_paths = img_paths
        self.img_col_content = ft.Column()
        self.update_content()

    def build(self):
        return self.img_col_content

    def update_content(self):
        self.img_col_content.controls.clear()
        to_insert_img_ls = []
        for path in self.img_paths:
            try:
                to_insert_img_ls.append(ft.Image(
                    src_base64=cv2_base64(read_image(path))
                ))
            except Exception as e:
                logger.error(f'ResultBody {path}传入出错\n{e}')
        self.img_col_content.controls.extend(to_insert_img_ls)


# 程序主界面
class CuttingErrorApp(ft.UserControl):
    def __init__(self, width: float, height: float):
        super().__init__()
        self.width, self.height = width, height  # 获取界面尺寸
        self.img_list = []  # 设置传入图像列表
        self.selected_image_item = None  # 被选中的图像

        # 顶部操作栏BEGIN
        self.pick_files_dialog = ft.FilePicker(on_result=self.select_images)  # 文件选择器
        self.top_bar = ft.Row(
            controls=[
                ft.ElevatedButton(text="批量选择要处理的图像文件",
                                  icon=ft.icons.IMAGE_SEARCH,  # 图标
                                  on_click=lambda _: self.pick_files_dialog.pick_files(
                                      allow_multiple=True,  # 是否允许多选
                                      allowed_extensions=[  # 允许的文件后缀名
                                          'jpg', 'png', 'tiff', 'webp', 'jfif', 'jpeg'
                                      ]
                                  )),
                ft.ElevatedButton("开始分析", icon=ft.icons.LINE_AXIS_ROUNDED),
            ],
            alignment=ft.MainAxisAlignment.CENTER
        )
        # 顶部操作栏END

        self.pb = ft.ProgressBar(visible=False)  # 进度条

        # 中间内容BEGIN
        self.thumb_img_ls = ft.Column(  # 1.缩略图列表
            spacing=5,
            scroll=ft.ScrollMode.ALWAYS,  # 设置显示滚动栏

        )
        self.main_content = ResultBody([], self)  # 2.中间显示图片目标检测内容

        self.result_panel = ResultPanel(self)  # 3.结果面板
        self.vertical_divider = ft.VerticalDivider(width=3)  # 垂直分隔符
        self.body = ft.Row(  # 中间内容合并
            controls=[
                ft.Container(
                    content=self.thumb_img_ls,
                    expand=2,  # expand设置占用比例
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
            alignment=ft.MainAxisAlignment.START,  # 靠左对齐
            spacing=0,
            # expand=True,
        )
        self.set_body_height()  # 设置缩略图显示列表
        self.update_thumbs()  # 更新缩略图显示
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

    def set_body_height(self):
        """
        根据窗口大小，自适应设置缩略图列表的高度
        :return: None
        """
        self.body.height = self.height - 120  # 设置窗口内容大小，将窗口大小减去一个值

    def set_pb_value(self, value: float = 1.0):
        """
        设置进度条值
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

            t = Timer(1, set_hidden)  # 延迟1s
            t.start()
        # 设置延迟消失END

    def set_size(self, size: tuple[float, float]):
        """
        调节窗口大小时，动态获得窗口尺寸
        :param size: 窗口尺寸，宽度和高度
        :return: None
        """
        self.width, self.height = size  # 获得传入窗口大小
        self.set_body_height()
        self.update()

    def update_thumbs(self):
        """
        更新缩略图列表
        :return: None
        """
        self.thumb_img_ls.controls.clear()  # 1.清除现有显示的缩略图内容
        to_insert_thumbs = []  # 2.确定需要插入的缩略图对象
        img_len = len(self.img_list)
        success_count = 0
        for name in self.img_list:
            try:
                to_insert_thumbs.append(ImageItem(
                    img_path=name,
                    parent=self
                ))
                success_count += 1
                self.set_pb_value(success_count / img_len)
            except Exception as e:
                logger.error(f'CuttingErrorApp {name}传入出错\n{e}')
                img_len -= 1
        minimum_to_show_img_num = 1  # 最小要显示图片数量
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

    def select_images(self, e: ft.FilePickerResultEvent):
        """
        选择需要上传的图片
        :param e: 点击对象
        :return: None
        """
        if not e.files:
            return None
        '''
        map(function,iterable,...)，即
        - 第一个参数为函数，这里使用了lambda表达式，表示要获取的文件路径；
        - 第二个参数为可迭代的对象，这里的e.files表示了传入的文件
        通过map映射获得了所有文件的文件名
        '''
        self.img_list = list(map(lambda f: f.path, e.files))
        self.update_thumbs()  # 更新缩略图
        self.update()


def ui(page: ft.Page):
    page.title = '液晶屏切割缺陷检测系统'
    page.window_width, page.window_height = 1000, 600  # 设置窗口初始化尺寸
    page.window_min_width, page.window_min_height = 700, 400  # 设置窗口最小可调整尺寸
    # page.bgcolor = ft.colors.PINK
    cutting_error_app = CuttingErrorApp(page.window_width, page.window_height)  # 初始化要显示的内容

    def page_resize(e):
        """
        窗口尺寸大小变化时监听事件
        :param e: 事件
        :return: None
        """
        size = page.window_width, page.window_height  # 获得当前窗口尺寸
        cutting_error_app.set_size(size)  # 对目标对象传入改变后的窗口尺寸大小

    page.on_resize = page_resize  # 设置窗口尺寸大小变化时的监听事件
    page.overlay.append(cutting_error_app.pick_files_dialog)  # 选择文件对话框
    page.add(
        cutting_error_app
    )
    # print(page.platform)


def show():
    ft.app(target=ui)
