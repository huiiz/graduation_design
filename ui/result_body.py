import flet as ft

from img_process.change_tiff import cv2_base64
from img_process.basic import read_image


# 结果主体内容，即最中间的图像显示部分。该部分的内容会随着左侧的图像缩略图的点击而改变，点击该部分会修改右侧上方的百分比
class ResultBody(ft.UserControl):
    def __init__(self, parent):
        super().__init__()
        # 演示数据
        self.parent = parent
        self.item_name = None
        self.ng_dt = {}
        self.img_paths = []
        self.percentages = []
        self.length = 0
        self.index = 0
        self.image_item = ft.Image(
            src_base64=cv2_base64(read_image('source/to_show_img.png')),
        )
        self.image_item_container = ft.Container(
            content=self.image_item,
            alignment=ft.alignment.center
        )
        self.text = ft.Text(
            value='0/0'
        )
        self.text_container = ft.Container(
            content=self.text,
            alignment=ft.alignment.top_center,
            expand=1
        )
        self.left_button = ft.IconButton(
            icon=ft.icons.ARROW_CIRCLE_LEFT_OUTLINED,
            icon_size=60,
            # icon_color=ft.colors.WHITE54,
            on_click=self.turn_left,
        )
        self.left_button_container = ft.Container(
            content=self.left_button,
            alignment=ft.alignment.center_left,
            expand=1
        )
        self.right_button = ft.IconButton(
            icon=ft.icons.ARROW_CIRCLE_RIGHT_OUTLINED,
            icon_size=60,
            # icon_color=ft.colors.WHITE54,
            on_click=self.turn_right,
        )
        self.right_button_container = ft.Container(
            content=self.right_button,
            alignment=ft.alignment.center_right,
            expand=1
        )
        self.buttons = ft.Row(
            controls=[
                self.left_button_container,
                self.right_button_container
            ],
        )
        self.set_buttons()
        self.img_col_content = ft.Stack(
            controls=[
                self.image_item_container,
                self.text_container,
                self.buttons
            ],
        )
        # self.update_content()

    def build(self):
        return self.img_col_content

    def set_item_name(self, name: str):
        self.item_name = name
        self.ng_dt = self.parent.defect_dt.get(self.item_name, {})
        ngs = sorted(self.ng_dt.items(), key=lambda x: x[1], reverse=True)
        self.img_paths = [f'temp/cut/{self.item_name}/{key}.png' for key in [ng[0] for ng in ngs]]
        self.percentages = [ng[1] * 100 for ng in ngs]
        self.length = len(self.img_paths)
        self.index = 0

    def turn_left(self, e):
        if self.index > 0:
            self.index -= 1
            self.update()

    def turn_right(self, e):
        if self.index < self.length - 1:
            self.index += 1
            self.update()

    def set_buttons(self):
        # 设置左右按钮的状态 set the state of left and right buttons
        if self.index == 0:
            self.left_button.disabled = True
        else:
            self.left_button.disabled = False
        if self.index == self.length - 1 or self.length == 0:
            self.right_button.disabled = True
        else:
            self.right_button.disabled = False

    def update(self):
        self.set_buttons()
        # 设置图片 set the image
        if self.length > 0:
            self.image_item.src_base64 = cv2_base64(read_image(self.img_paths[self.index]))

        # 设置文字 set the text
        self.text.value = f'{self.index + 1 if self.length > 0 else self.index}/{self.length}'

        self.parent.result_panel.item_name = self.item_name
        self.parent.result_panel.percentage = self.percentages[self.index] if self.length > 0 else 0
        self.parent.result_panel.update()
        super().update()
