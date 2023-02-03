from change_tiff import cv2_base64, change_tiff_into_thumb

import flet as ft


# 图像缩略图中单个图像
class ImageItem(ft.UserControl):
    def __init__(self, img_path: str, main_content: ft.container.Container, name: str = None):
        """
        初始化缩略图对象
        :param img_path: 传入图像本地地址
        :param main_content: 处理结果容器
        :param name: 图像名称，可不填
        """
        super().__init__()
        self.img_name = name if name else img_path.split('\\')[-1]
        self.img_base64 = cv2_base64(image=change_tiff_into_thumb(img_path=img_path, new_size=150))
        self.main_content = main_content
        self.selected = False

    def build(self):
        return ft.Container(
            content=ft.Stack(
                controls=[
                    ft.Image(
                        src_base64=self.img_base64,
                        fit=ft.ImageFit.CONTAIN,
                    ),
                    ft.Container(
                        content=ft.Text(
                            value=self.img_name,
                            color=ft.colors.BLACK,
                            size=12,
                            weight=ft.FontWeight.BOLD,
                        ),
                        alignment=ft.alignment.top_center,
                        bgcolor=ft.colors.ORANGE_200,
                        opacity=0.5
                    ),
                ],
            ),
            on_click=self.click,
            border=ft.border.all(1, ft.colors.BLACK38),
            width=102,
            on_hover=self.on_hover,
        )

    def set_text_attr(self, attr: str, value: str | float, e: ft.control_event.ControlEvent):
        """
        设置文本对象的属性
        :param attr: 待设置属性
        :param value: 待设置属性值
        :param e: 要处理对象
        :return: None
        """
        match attr:
            case 'bgcolor':
                print('kkk')
                e.control.content.controls[1].bgcolor = value
            case 'opacity':
                e.control.content.controls[1].opacity = value
            case 'color':
                e.control.content.controls[1].content.color = value
            case default:
                return None
        e.control.update()

    def set_selected_status(self, e):
        """
        将本缩略图设置为选中状态
        :param e: 要处理的对象
        :return: None
        """
        self.set_text_attr('bgcolor', ft.colors.ORANGE_500, e)
        self.set_text_attr('opacity', 0.8, e)
        self.set_text_attr('color', ft.colors.WHITE, e)

    def set_cancel_selected_status(self, e):
        """
        将本缩略图设置为取消选中状态
        :param e: 要处理的对象
        :return: None
        """
        self.set_text_attr('bgcolor', ft.colors.ORANGE_200, e)
        self.set_text_attr('opacity', 0.5, e)
        self.set_text_attr('color', ft.colors.BLACK, e)

    def on_hover(self, e: ft.control_event.ControlEvent):
        """
        单个缩略图hover事件
        :param e: hover对象
        :return: None
        """
        # print(str(e))
        match e.data:
            case 'true':
                self.set_selected_status(e)
            case 'false':
                if not self.selected:
                    self.set_cancel_selected_status(e)
            case default:
                return None

    def click(self, e: ft.control_event.ControlEvent):
        """
        单个缩略图点击事件
        :param e: 点击对象
        :return: None
        """
        self.selected = True
        self.set_selected_status(e)
        self.main_content.content = ft.Text(f'点击了{self.img_name}')
        self.main_content.update()


# 程序主界面
class CuttingErrorApp(ft.UserControl):
    def __init__(self):
        super().__init__()
        self.result_panel = None
        self.body = None
        self.top_bar = None
        self.main_content = ft.Container(
            content=ft.Text('处理结果将在这里显示', bgcolor=ft.colors.GREEN_50),
        )
        self.thumb_img_ls = ft.ListView(
                spacing=5,
                height=400,
                # horizontal_alignment=ft.CrossAxisAlignment.CENTER
            )
        self.img_list = []
        self.pick_files_dialog = ft.FilePicker(on_result=self.select_images)
        self.vertical_divider = ft.VerticalDivider()
        self.selected_image_item = None

    def build(self):
        self.top_bar = ft.Row(
            controls=[
                ft.ElevatedButton("批量选择要处理的图像文件", icon=ft.icons.IMAGE_SEARCH,
                                  on_click=lambda _: self.pick_files_dialog.pick_files(allow_multiple=True)),
                ft.ElevatedButton("开始分析", icon=ft.icons.LINE_AXIS_ROUNDED),
            ],
            alignment=ft.MainAxisAlignment.CENTER
        )
        self.result_panel = ft.Column(
            controls=[
                ft.Text('结果面板')
            ],

        )
        self.update_thumbs()
        self.body = ft.Row(
            controls=[
                ft.Container(
                    content=self.thumb_img_ls,
                    expand=1
                ),
                ft.Container(
                    content=self.main_content,
                    expand=5
                ),
                ft.Container(
                    content=self.result_panel,
                    expand=2
                ),
            ],
            alignment=ft.MainAxisAlignment.START
        )
        return ft.Column(
            controls=[
                self.top_bar,
                self.body
            ],
        )

    def update_thumbs(self):
        """
        更新缩略图列表
        :return: None
        """
        self.thumb_img_ls.controls.clear()
        to_insert_thumbs = [ImageItem(name, self.main_content) for name in self.img_list]
        minimum_to_show_img_num = 1  # 最小要显示图片数量
        if len(to_insert_thumbs) < minimum_to_show_img_num:
            to_insert_thumbs.extend([ImageItem('source\\to_show_img.png', self.main_content, '选择要处理图片') for _ in
                                     range(minimum_to_show_img_num - len(to_insert_thumbs))])
        self.thumb_img_ls.controls.extend(to_insert_thumbs)

    def select_images(self, e: ft.FilePickerResultEvent):
        """
        选择需要上传的图片
        :param e: 点击对象
        :return: None
        """
        if not e.files:
            return None
        self.img_list = list(map(lambda f: f.path, e.files))
        self.update_thumbs()
        self.update()

    def get_selected_item(self):
        pass


def main(page: ft.Page):
    page.title = '切割异常检测系统'
    page.window_width = 1000
    page.window_height = 600
    cutting_error_app = CuttingErrorApp()
    page.overlay.append(cutting_error_app.pick_files_dialog)
    page.add(
        cutting_error_app
    )
    # print(page.platform)


ft.app(target=main)
