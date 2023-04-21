import flet as ft

from report.result import HtmlReport
from ui.manual_annotation import ManualAnnotation


# 结果显示控制面板，包括裁决该图像是否为切割异常，以及导出与显示最终结果
class ResultPanel(ft.UserControl):
    def __init__(self, parent):
        """
        初始化结果控制面板
        :param parent:
        """
        super().__init__()
        self.item_name: str = ''  # 当前图像名字 current image name
        self.image_path: str = ''  # 当前图像路径 current image path
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
            value='本图最终结果为：?',
        )
        self.change_button = ft.ElevatedButton(  # 点击修改结果按钮 click the button to change the result
            text='点击修改最终结果',
            on_click=self.change_result,
        )
        self.manual_annotation_button = ft.ElevatedButton(  # 点击修改结果按钮 click the button to change the result
            text='手工标注',
            on_click=self.manual_annotation
        )
        self.manual_annotation_tip = ft.Text(
            value='未手工标注',
            color=ft.colors.BLUE
        )
        self.manual_annotation_row1 = ft.Row(
            controls=[
                self.manual_annotation_button,
                self.manual_annotation_tip
            ],
            alignment=ft.MainAxisAlignment.CENTER
        )
        self.cancel_annotation_button = ft.ElevatedButton(
            text='取消标注',
            on_click=self.cancel_annotation
        )
        self.save_annotation_button = ft.ElevatedButton(
            text='保存标注',
            on_click=self.save_annotation
        )

        self.manual_annotation_row2 = ft.Row(
            controls=[
                self.cancel_annotation_button,
                self.save_annotation_button
            ],
            alignment=ft.MainAxisAlignment.CENTER
        )

        self.to_show_annotation_button = ft.Container(
            content=self.manual_annotation_row1,
        )

        self.item_result_control_panel = ft.Column(
            controls=[
                ft.Container(
                    self.predict_percentage,
                    alignment=ft.alignment.center
                )
            ],
            alignment=ft.MainAxisAlignment.CENTER
        )

        self.single_control_panel = ft.Column(
            controls=[
                ft.Container(
                    self.predict_result,
                    alignment=ft.alignment.center
                ),
                ft.Container(
                    self.final_result,
                    alignment=ft.alignment.center
                ),
                ft.Container(
                    self.change_button,
                    alignment=ft.alignment.center
                ),
                self.to_show_annotation_button
            ],
            alignment=ft.MainAxisAlignment.CENTER
        )
        # 单图部分END

        # 所有图像部分BEGIN
        self.all_result = ft.Text(  # 整体数量部分
            value='本批共选中?张样品图像，已完成检测0张，其中?张为存在缺陷样品，?张为正常样品'
        )
        # self.show_result = ft.ElevatedButton(  # 预览结果
        #     text='预览结果',
        #     on_click=None
        # )
        self.show_report = ft.Checkbox(
            label='保存检测报告后是否打开进行预览？',
            value=True
        )
        self.export_result = ft.ElevatedButton(  # 保存结果为文件
            text='保存检测报告',
            on_click=self.save_result
        )
        self.all_control_panel = ft.Column(
            controls=[
                ft.Container(
                    self.all_result,
                    alignment=ft.alignment.center
                ),
                # ft.Container(
                #     self.show_result,
                #     alignment=ft.alignment.center
                # ),
                ft.Container(
                    self.show_report,
                    alignment=ft.alignment.center
                ),
                ft.Container(
                    self.export_result,
                    alignment=ft.alignment.center
                )
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


    def check_img_ls_exist(func):
        def check(self, *args, **kwargs):
            if not self.parent.predict_result:
                self.parent.set_tip_value('请先选择要处理的图片')
                return
            func(self, *args, **kwargs)
        return check

    @check_img_ls_exist
    def manual_annotation(self, e):
        """
        手动标注
        :return:
        """
        self.parent.manual_annotation_control.content = ManualAnnotation(self.image_path, self.parent)
        self.parent.manual_annotation_control.update()
        self.parent.main_content_tabs.selected_index = 1
        self.parent.main_content_tabs.update()
        self.to_show_annotation_button.content = self.manual_annotation_row2
        self.to_show_annotation_button.update()

    @check_img_ls_exist
    def cancel_annotation(self, e):
        """
        取消标注
        :return:
        """
        self.manual_annotation_tip.value = '未手工标注'
        self.manual_annotation_tip.update()
        self.parent.manual_annotation.pop(self.item_name, None)
        self.to_show_annotation_button.content = self.manual_annotation_row1
        self.to_show_annotation_button.update()
        self.parent.main_content_tabs.selected_index = 0
        self.parent.main_content_tabs.update()
        self.parent.final_result[self.item_name] = self.parent.predict_result[self.item_name]
        self.update()

    @check_img_ls_exist
    def save_annotation(self, e):
        """
        保存标注
        :return:
        """
        abs_points = self.parent.manual_annotation_control.content.get_abs_pos()
        if abs_points[2] is None:
            self.parent.set_tip_value('请先进行标注再保存')
            return
        self.manual_annotation_tip.value = '已完成手工标注'
        self.manual_annotation_tip.update()
        self.parent.manual_annotation[self.item_name] = abs_points
        print(self.parent.manual_annotation)
        self.to_show_annotation_button.content = self.manual_annotation_row1
        self.to_show_annotation_button.update()
        self.parent.main_content_tabs.selected_index = 0
        self.parent.main_content_tabs.update()
        self.update()

    @check_img_ls_exist
    def change_result(self, e):
        """
        修改预测结果
        :return:
        """
        if self.parent.main_content_tabs.selected_index == 1:
            return # 如果当前是单图模式，不允许修改预测结果
        if self.item_name not in self.parent.manual_annotation:
            self.parent.final_result[self.item_name] = not self.parent.final_result[self.item_name]
            self.update()
        else:
            self.parent.final_result[self.item_name] = self.parent.predict_result[self.item_name]
            self.parent.set_tip_value('该图片已手动标注，需取消标注后才能修改预测结果')
            self.update()

    def save_result(self, e):
        """
        保存结果
        :return:
        """
        if not self.parent.img_list:
            self.parent.set_tip_value('请先选择要处理图片!')
            return
        if not self.parent.begin_to_process:
            self.parent.set_tip_value('请先处理图片!')
            return
        if len(self.parent.predict_result) != len(self.parent.img_list):
            self.parent.set_tip_value('请等待处理完成!')
            return
        if self.parent.main_content_tabs.selected_index == 1:
            self.parent.set_tip_value('请先退出手工标注模式!')
            return

        html_report = HtmlReport(self.parent)
        res_fname = html_report.save_and_show_html(self.show_report.value)
        self.parent.set_tip_value(f'检测报告已保存至{res_fname}文件中')

    def reset(self):
        self.item_name = ''
        self.image_path = ''
        self.percentage = 0
        self.predict_percentage.value = '本区域为切割异常的可能性为：?%'
        self.predict_result.value = '根据算法，本图预测结果为：?'
        self.final_result.value = '本图最终结果为：?'
        self.all_result.value = '本批共选中?张样品图像，已完成检测0张，其中?张为存在缺陷样品，?张为正常样品'
        super().update()

    def update(self):
        predict_defect = self.parent.predict_result.get(self.item_name, {})
        final_predict_defect = self.parent.final_result.get(self.item_name, {}) or \
                               (self.item_name in self.parent.manual_annotation)
        final_ls = [v or (k in self.parent.manual_annotation) for k, v in self.parent.final_result.items()]
        # print(self.item_name, self.parent.final_result, self.parent.manual_annotation, final_predict_defect, final_ls)

        self.predict_percentage.value = f'本区域为切割异常的可能性为：{round(self.percentage, 2)}%'
        self.predict_result.value = f'根据算法，本图预测结果为：{"有缺陷" if predict_defect else "正常"}'
        self.final_result.value = f'本图最终结果为：{"有缺陷" if final_predict_defect else "正常"}'
        normal_count = final_ls.count(False)
        defect_count = final_ls.count(True)
        total_count = len(self.parent.img_list)
        processed_count = len(self.parent.final_result)
        self.all_result.value = f'本批共选中{total_count}张样品图像，已完成检测{processed_count}张，其中{defect_count}张为存在缺陷样品，{normal_count}张为正常样品'
        super().update()
