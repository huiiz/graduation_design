import flet as ft

from img_process.basic import get_img_size, read_image
from img_process.change_tiff import cv2_base64

w_dif = 6 + 2 * 10
h_dif = 40 + 90 + 7 + 3 * 10


# 人工标注图像
class ManualAnnotation(ft.UserControl):
    def __init__(self, img_path: str, parent):
        """
        初始化人工标注类
        :param img_path: 要标注的图像路径
        :param parent:
        """
        super().__init__()
        # parent.window_height, parent.window_width = 650, 450
        # parent.window_left, parent.window_top = 400, 20
        # parent.title = '人工标注缺陷部位'
        # parent.padding = 0
        # parent.window_width, parent.window_height = 1000, 600  # 设置窗口初始化尺寸 set the initial size of the window
        # parent.window_min_width, parent.window_min_height = 400, 300  # 设置窗口最小可调整尺寸 set the minimum size of the window

        self.img_path = img_path
        self.parent = parent
        self.change_y = 0  # 在本宽度下，下滑距离
        self.old_change_y = 0  # 上一次下滑距离
        self.change_y_per = 0  # 下滑距离百分比
        self.old_change_y_per = 0  # 上一次下滑距离百分比
        self.points = [None for _ in range(4)]  # 记录框选的四个点
        parent.parent.on_resize = self.page_resize
        self.c = ft.Container()  # 用于显示框选的矩形
        # 鼠标操作
        self.g_block = ft.GestureDetector(
            mouse_cursor=ft.MouseCursor.PRECISE,
            on_pan_start=self.start,
            on_pan_update=self.update_r,
            on_pan_end=self.end,
            # on_tap=click,
            on_secondary_tap=self.click,  # 右击取消框选
            on_scroll=self.scroll,
            # drag_interval=50,
        )
        self.g = ft.Container(
            self.g_block,
            width=parent.width * 15 / 23 - w_dif,
            height=parent.height - h_dif,
            # border=ft.border.all(0),
            alignment=ft.alignment.center_right
        )
        # name = "ScanImage_Image0 (6).tiff"
        self.w, self.h = get_img_size(self.img_path)  # 图像宽高
        # print(self.w, self.h)
        # print(self.img_path)
        # 显示图像
        self.img = ft.Image(
            src=self.img_path,
            # src_base64=cv2_base64(
            #     image=read_image(self.img_path),
            # ),
            fit=ft.ImageFit.FIT_WIDTH,
            offset=ft.transform.Offset(0, 0),
            width=self.g.width,
            height=self.h / (self.w / self.g.width),  # 根据比例设置图像高度
        )
        # 将图像放在Column中，使其可以完整显示
        self.img_column = ft.Column(
            [self.img],
            scroll=ft.ScrollMode.HIDDEN,
            alignment=ft.MainAxisAlignment.START
        )
        self.img_c = ft.Container(
            self.img_column,
            width=self.g.width,
            height=self.g.height,
            top=0,
            # alignment=ft.alignment.top_left,
            padding=0,
            offset=ft.transform.Offset(0, 0),
        )
        # 使用stack，将画的矩形框和鼠标操作放在一起
        self.c_g_stack = ft.Stack([self.c, self.g])
        self.t_c_g = ft.Container(self.c_g_stack)

    def page_resize(self, e):
        old_w, old_h = self.g.width, self.g.height
        self.g.width, self.g.height = self.parent.width * 15 / 23 - w_dif, self.parent.height - h_dif
        self.g.update()
        # print(self.parent.main_content.width)
        self.img.width = self.g.width
        self.img.height = self.h / (self.w / self.g.width)
        self.img.offset = ft.transform.Offset(0, -1 * self.change_y_per)  # 设置窗口大小变化时，图像的偏移
        self.change_y = self.change_y_per * self.img.height  # 更新下滑距离
        self.old_change_y = self.old_change_y_per * self.img.height  # 更新下滑距离
        self.img.update()

        self.img_c.width, self.img_c.height = self.g.width, self.g.height
        self.img_c.update()
        if self.points[2] is not None and old_w != self.g.width:
            self.points = [i * self.g.width / old_w for i in self.points]
            self.update_rectangle()
            # print('resize points update!', self.points)
            # print(self.points)

    def click(self, e):
        """
        鼠标右击时，删除矩形框
        :param e:
        :return:
        """
        self.del_rectangle()

    def del_rectangle(self):
        self.points = [None for _ in range(4)]
        self.c.width = None
        self.c.height = None
        self.c.border = None
        self.c.update()

    def update_rectangle(self):
        """
        更新矩形框
        :return:
        """
        if self.points[0] is not None and self.points[3] is not None:
            self.c.left = self.points[1]
            self.c.top = self.points[0]
            self.c.width = self.points[3] - self.points[1]
            self.c.height = self.points[2] - self.points[0]
            self.c.update()

    def get_abs_pos(self):
        """
        计算获得矩形框在图像中
        :return: left, top, right, bottom
        """
        if self.points[3] is None:
            return [None for _ in range(4)]
        offset = self.change_y * self.w / self.g.width
        abs_p = [None for _ in range(4)]
        abs_p[1] = self.points[1] * self.w / self.g.width
        abs_p[3] = self.points[3] * self.w / self.g.width
        abs_p[0] = offset + self.points[0] * self.w / self.g.width
        abs_p[2] = offset + self.points[2] * self.w / self.g.width
        abs_p = list(map(int, abs_p))
        return abs_p[0], abs_p[2], abs_p[1], abs_p[3]

    def scroll(self, e: ft.ScrollEvent):
        # print(self.g.width, self.g.height)
        delta_y = 0.2 * self.g.height if e.scroll_delta_y > 0 else -1 * 0.2 * self.g.height
        self.change_y += delta_y
        self.change_y = max(0., min(self.img.height - self.g.height, self.change_y))
        self.change_y_per = self.change_y / self.img.height
        # print(change_y_per)
        self.img.offset = ft.transform.Offset(0, -1 * self.change_y_per)
        self.img.update()
        # print(self.old_change_y, self.change_y)
        if self.points[0] is not None and self.points[2] is not None and self.old_change_y != self.change_y:
            # print('change')
            # print(self.points)
            delta1 = self.change_y - self.old_change_y
            self.points[0] -= delta1
            self.points[2] -= delta1
            # print('scroll update!', self.points)
            self.update_rectangle()
            # print('-' * 40)

        self.old_change_y = self.change_y
        self.old_change_y_per = self.change_y_per

        # print(res, max_v)

    def start(self, e: ft.DragUpdateEvent):
        self.points = [e.local_y, e.local_x, None, None]
        # print(img.height)

    def update_r(self, e: ft.DragUpdateEvent):
        self.c.border = ft.border.all(2, ft.colors.RED)
        if self.points[1] > e.local_x:  # 新点在当前点的左边，则固定右边
            self.c.left = None
            self.c.right = self.g.width - self.points[1]
        else:
            self.c.right = None
            self.c.left = self.points[1]
        if self.points[0] > e.local_y:  # 新点在当前点的上边，则固定下边
            self.c.top = None
            self.c.bottom = self.g.height - self.points[0]
            # print(c.bottom)
            # print(page.height, points[1], c.height)
        else:
            self.c.bottom = None
            self.c.top = self.points[0]
        self.c.width = abs(e.local_x - self.points[1])
        self.c.height = abs(e.local_y - self.points[0])
        self.points[3] = e.local_x
        self.points[2] = e.local_y
        self.c.update()
        # print("update", e.global_x, e.global_y, page.height, c.bottom)

    def end(self, e: ft.DragEndEvent):
        print('坐标', self.get_abs_pos())
        pass

    def build(self):
        return ft.Stack([self.img_c, self.t_c_g])
