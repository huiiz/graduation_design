import base64

from jinja2 import Environment, FileSystemLoader
import time
import os

from check.check_defect import get_defect_imgs_dt
from img_process.basic import get_image_by_range, read_image
from img_process.change_tiff import cv2_base64


class HtmlReport:
    def __init__(self, cutting_error_app):
        # 图片路径列表
        self.img_list = cutting_error_app.img_list
        # 图片名字-路径字典
        self.name_path_dt = cutting_error_app.name_path_dt
        # 图片名字列表
        self.img_names = list(cutting_error_app.name_path_dt.keys())
        # 缺陷区块, key: 图片名字, value: 缺陷概率字典,k: 缺陷区块左上角坐标, v: 缺陷概率
        self.defect_dt = cutting_error_app.defect_dt
        # 预测结果, key: 图片名字, value: 是否为缺陷,True为缺陷
        self.predict_result = cutting_error_app.predict_result
        # 最终结果, key: 图片名字, value: 是否为缺陷,True为缺陷
        self.final_result = cutting_error_app.final_result
        # 手动标注结果, key: 图片名字, value: 缺陷坐标,(r1,r2,c1,c2)
        self.manual_annotation = cutting_error_app.manual_annotation
        # 为每个名字编造id
        self.ids = {name: f'img_{self.base_16(name)}' for name in self.img_names}

    @staticmethod
    def base_16(text: str):
        text_bytes = text.encode('utf-8')
        base16_bytes = base64.b16encode(text_bytes)
        base16_text = base16_bytes.decode('utf-8')
        return base16_text

    @property
    def total_count(self):
        return len(self.img_list)

    @property
    def predict_defect_count(self):
        return len([v for v in self.predict_result.values() if v])

    @property
    def changed_count(self):
        return len([k for k, v in self.final_result.items() if self.predict_result[k] != v])

    @property
    def manual_annotation_count(self):
        return len(self.manual_annotation)

    @property
    def final_defect_count(self):
        return len([v for k, v in self.final_result.items() if v or (k in self.manual_annotation)])

    @property
    def description(self):
        return f"""本轮共检测了{self.total_count}份样本,其中{self.predict_defect_count}份被自动判断为缺陷样本,
        {self.changed_count}份自动检测样本结果被手动修改,{self.manual_annotation_count}份被手动标注为缺陷样本,
        最终{self.final_defect_count}份标记为缺陷样本。各样本标记情况如下:"""

    @property
    def html_table_head(self):
        return """<table border="1" align="center" class="restable">
        <thead>
        <tr>
        <th>图片名</th>
        <th>算法预测结果</th>
        <th>缺陷部位最大可能性</th>
        <th>手动修改预测结果?</th>
        <th>手动标注缺陷?</th>
        <th>最终结果</th>
        </tr>
        </thead>
        <tbody>"""

    def get_html_table_line(self, img_name: str, predict_result: bool, defect_possibility: float,
                            changed: bool, manual_annotation: bool, final_result: bool):
        return f"""<tr onclick="window.location.href='#{self.ids[img_name]}';">
        <td>{img_name}</td>
        <td>{'有缺陷' if predict_result else '无缺陷'}</td>
        <td>{defect_possibility * 100 :.2f}%</td>
        <td>{'✔' if changed else '✘'}</td>
        <td>{'✔' if manual_annotation else '✘'}</td>
        <td>{'有缺陷' if final_result else '无缺陷'}</td>
        </tr>"""

    def get_each_line_data(self, img_name):
        predict_result = self.predict_result[img_name]
        defect_possibility = max(self.defect_dt[img_name].values()) if len(self.defect_dt[img_name].values()) > 0 else 0.
        changed = self.predict_result[img_name] != self.final_result[img_name]
        manual_annotation = img_name in self.manual_annotation
        final_result = self.final_result[img_name] or manual_annotation
        return predict_result, defect_possibility, changed, manual_annotation, final_result

    @property
    def table_html(self):
        html_table = self.html_table_head
        for img_name in self.img_names:
            predict_result, defect_possibility, changed, manual_annotation, final_result = self.get_each_line_data(img_name)
            html_table += self.get_html_table_line(img_name, predict_result, defect_possibility, changed, manual_annotation, final_result)
        html_table += '</tbody></table>'
        return html_table

    @property
    def processed_defect_dt(self):
        processed_data = {}
        for k, v in self.defect_dt.items():
            data = []
            for place, possibility in v.items():
                each = {}
                each['possibility'] = f'{possibility* 100 :.2f}'
                r1, c1 = map(int, place.split('_'))
                each['points'] = r1, r1+512, c1, c1+512
                img_data = get_defect_imgs_dt(k, place)
                each['img_base64'] = cv2_base64(img_data)
                data.append(each)
            processed_data[k] = data
        return processed_data

    @property
    def processed_manual_annotation(self):
        processed_data = {}
        for k, v in self.manual_annotation.items():
            data = {}
            data['points'] = v
            img_path = self.name_path_dt[k]
            image_data = get_image_by_range(read_image(img_path), v)
            data['img_base64'] = cv2_base64(image_data)
            processed_data[k] = data
        return processed_data

    def get_html(self, time_str: str):
        env = Environment(loader=FileSystemLoader('source'))
        template = env.get_template('template.html')
        html = template.render(report_datetime=time_str, description=self.description, table=self.table_html,
                               name_path_dt=self.name_path_dt, img_names=self.img_names, ids=self.ids,
                               predict_result=self.predict_result, final_result=self.final_result,
                               defect_dt=self.processed_defect_dt, manual_annotation=self.processed_manual_annotation)
        return html

    def save_and_show_html(self, show=True):
        # 时间戳
        time_stamp = time.time()
        file_time_str = time.strftime('%Y-%m-%d-%H-%M-%S', time.localtime(time_stamp))
        show_time_str = time.strftime('%Y年%m月%d日 %H:%M:%S', time.localtime(time_stamp))

        html = self.get_html(show_time_str)
        with open(f'temp\\report\\{file_time_str}.html', 'w', encoding='utf-8') as f:
            f.write(html)
        if show:
            os.startfile(f'temp\\report\\{file_time_str}.html')
        return f'{file_time_str}.html'


