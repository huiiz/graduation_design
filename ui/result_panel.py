import flet as ft


# 结果显示控制面板，包括裁决该图像是否为切割异常，以及导出与显示最终结果
class ResultPanel(ft.UserControl):
    def __init__(self, parent):
        """
        初始化结果控制面板
        :param parent:
        """
        super().__init__()
        self.item_name: str = ''  # 当前图像名字 current image name
        self.parent = parent

        self.percentage = 0

        # 单图部分BEGIN
        self.predict_percentage = ft.Text(  # 显示区块为切割异常的可能性 show the possibility of the block is cut abnormal
            value='本区域为切割异常的可能性为：?%'
        )
        self.predict_result = ft.Text(  # 显示当前图片文件预测是否为切割异常的结果 show the result of the current image file is cut abnormal
            value='预测结果为：?'
        )
        self.final_result = ft.Text(
            # 显示当前图片文件最终是否为切割异常的结果 show the final result of the current image file is cut abnormal
            value='本图最终结果为：?'
        )
        self.change_button = ft.ElevatedButton(  # 点击修改结果按钮 click the button to change the result
            text='预测结果错误，点击修改',
            on_click=self.change_result
        )
        self.item_result_control_panel = ft.Column(
            controls=[
                self.predict_percentage
            ],
            alignment=ft.MainAxisAlignment.CENTER
        )

        self.single_control_panel = ft.Column(
            controls=[
                self.predict_result,
                self.final_result,
                self.change_button
            ],
            alignment=ft.MainAxisAlignment.CENTER
        )
        # 单图部分END

        # 所有图像部分BEGIN
        self.all_result = ft.Text(  # 整体数量部分
            value='本批共选中?张样品图像，已完成检测0张，其中?张为存在缺陷样品，?张为正常样品'
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
                    content=self.item_result_control_panel
                ),
                ft.Divider(),  # 水平分割线
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

    def change_result(self, e):
        """
        修改预测结果
        :return:
        """
        self.parent.final_result[self.item_name] = not self.parent.final_result[self.item_name]
        self.update()

    def reset(self):
        self.item_name = ''
        self.percentage = 0
        self.predict_percentage.value = '本区域为切割异常的可能性为：?%'
        self.predict_result.value = '根据算法，本图预测结果为：?'
        self.final_result.value = '本图最终结果为：?'
        self.all_result.value = '本批共选中?张样品图像，已完成检测0张，其中?张为存在缺陷样品，?张为正常样品'
        super().update()

    def update(self):
        predict_defect = self.parent.predict_result.get(self.item_name, {})
        final_predict_defect = self.parent.final_result.get(self.item_name, {})
        self.predict_percentage.value = f'本区域为切割异常的可能性为：{round(self.percentage, 2)}%'
        self.predict_result.value = f'根据算法，本图预测结果为：{"有缺陷" if predict_defect else "正常"}'
        self.final_result.value = f'本图最终结果为：{"有缺陷" if final_predict_defect else "正常"}'
        normal_count = list(self.parent.final_result.values()).count(False)
        defect_count = list(self.parent.final_result.values()).count(True)
        total_count = len(self.parent.img_list)
        processed_count = len(self.parent.final_result)
        self.all_result.value = f'本批共选中{total_count}张样品图像，已完成检测{processed_count}张，其中{defect_count}张为存在缺陷样品，{normal_count}张为正常样品'
        super().update()
