import flet as ft
from img_process.change_tiff import cv2_base64, change_tiff_into_thumb
from utils import get_image_name_from_path


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
        self.img_name = get_image_name_from_path(img_path)  # 设置该缩略图对象的图像名字
        self.img_base64 = cv2_base64(
            image=change_tiff_into_thumb(img_path=img_path, new_size=200)  # 获得图像一定大小缩略图的编码为base64格式的数据
        )
        self.parent = parent  # 设置调用该对象的父类
        self.main_content = parent.main_content  # 获取父类对应显示
        self.image_path = img_path  # 设置要处理的图像地址
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

    def click(self, e=None):
        """
        单个缩略图点击事件 single thumbnail click event
        :param e: 点击对象
        :return: None
        """
        if self.img_name == 'to_show_img':
            self.parent.set_tip_value('请先选择图片！')
            return
        if not self.parent.begin_to_process:  # 如果还没有开始处理
            self.parent.set_tip_value('请先处理数据！')
            return
        elif self.img_name not in self.parent.defect_dt:  # 如果有缺陷数据，但是缺陷数据的数量小于图像数量
            self.parent.set_tip_value('该图片正在处理，请等待处理完成再查看结果！')
            return
        if self.parent.selected_image_item:  # 如果调用父类中已经有选中的缩略图对象
            if self.parent.selected_image_item is self:  # 判断选中的缩略图是不是当前这个
                return
            self.parent.selected_image_item.selected = False  # 取消原对象的选中状态
            self.parent.selected_image_item.set_cancel_selected_status()  # 将原对象样式调整为未选中状态
        self.selected = True  # 将当前对象设为选中状态
        self.parent.selected_image_item = self  # 将调用父类选中缩略图对象设置为本对象
        self.set_selected_status()  # 设置当前对象样式为选中状态
        self.main_content.set_item_name(self.img_name, self.image_path)
        self.main_content.update()
        self.parent.main_content_tabs.selected_index = 0
        self.parent.manual_annotation_control.content = ft.Text('请点击手工标注按钮')
        self.parent.main_content_tabs.update()
        self.parent.result_panel.to_show_annotation_button.content = self.parent.result_panel.manual_annotation_row1
        self.parent.result_panel.to_show_annotation_button.update()
