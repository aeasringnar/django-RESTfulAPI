import os
import time
from io import BytesIO
from pathlib import Path
from uuid import uuid4
import imgkit
import pdfkit
import pandas as pd
from pyecharts.components import Table
from pyecharts.options import ComponentTitleOpts
from bs4 import BeautifulSoup
from tempfile import NamedTemporaryFile
from shutil import copyfile
from typing import Union, Tuple


CSS_STYLE = '''
body {
    margin: 16px
}

table {
    /* margin: 20px; */
    border-radius: 5px;
    font-size: 12px;
    border: none;
    border-collapse: collapse;
    max-width: 100%;
    white-space: nowrap;
    word-break: keep-all;
    text-align: center;
    width: 800px;
}

table th {
    font-size: 20px;
    background-color: #F6F6F6;
}

table tr {
    display: table-row;
    vertical-align: inherit;
    border-color: inherit;
}

table tr:hover td {
    background: #00d1b2;
    color: #F8F8F8;
}

table td, table th {
    border-style: none;
    border-top: 1px solid #dbdbdb;
    border-left: 1px solid #dbdbdb;
    border-bottom: 1px solid #dbdbdb;
    border-right: 1px solid #dbdbdb;
    padding: .5em .55em;
    font-size: 15px;
}

table td {
    border-style: none;
    font-size: 17px;
    vertical-align: middle;
    border-bottom: 1px solid #dbdbdb;
    border-left: 1px solid #dbdbdb;
    border-right: 1px solid #dbdbdb;
    height: 30px;
}

table td:first-child {
    width: 75px;
}

table td:last-child {
    width: 75px;
}

table tr:nth-child(even) {
    background: #F6FBFF;
}

.title {
    margin-bottom: 12px;
}
'''


class TableToImg:
    '''将DataFrame对象转为PNG的文件流对象'''

    current_dir = Path(__file__).absolute().parent

    def __init__(self, table_title: str, headers: list, rows: list, wkimg_path: str = None, wkpdf_path: str = None) -> None:
        '''初始化工具类
        args：
            table_titile str：设置导入图片的标题
            datas DataFrame：设置要导出的数据
            wkimg_path str：用于配置wkhtmltoimage工具的可执行文件路径
            wkpdf_path str：用于配置wkhtmltopdf工具的可执行文件路径
        returns：
            None
        '''
        # 在默认样式中表格设置的宽度为800px，由于html的body存在margin=8px。所以输出图片时应当设置宽度为816px
        self.table_css_style = CSS_STYLE
        self.table_title = table_title
        self.headers = headers
        self.rows = rows
        self.imgkit_conf = imgkit.config(
            wkhtmltoimage=wkimg_path) if wkimg_path else None
        self.pdfkit_conf = pdfkit.configuration(
            wkhtmltopdf=wkpdf_path) if wkpdf_path else None
        self.imgkit_options = {
            'format': 'png',
            # 'crop-h': '400',
            'crop-w': '832',
            'crop-y': '0',
            'crop-x': '0',
            'encoding': "UTF-8",
        }
        self.pdfkit_options = {
            "encoding": "UTF-8",
            'margin-top': '0.75in',
            'margin-right': '0.75in',
            'margin-bottom': '0.75in',
            'margin-left': '0.75in',
        }

    def to_html(self) -> Tuple[bool, Union[None, str], str]:
        '''处理数据，将数据转为目标html的str内容'''
        try:
            table = Table()
            table.add(headers=self.headers, rows=self.rows)
            table.set_global_opts(
                title_opts=ComponentTitleOpts(title=self.table_title)
            )
            # 构建好相关的中转文件，后面会删除，由于pyecharts、imgkit、bs4并没有给读文件流和输出文件流的方式，因此这里只能使用文件中转
            # 使用临时文件实现
            # 创建临时文件
            tmp_file = NamedTemporaryFile()
            # 输出表格到临时文件
            table.render(tmp_file.name)
            soup = BeautifulSoup(tmp_file.read(), 'html.parser')
            for item in soup.find_all('style'):
                item.string = self.table_css_style
            return True, soup.prettify(), 'ok'
        except Exception as e:
            return False, None, str(e)

    def to_png(self) -> Tuple[bool, Union[None, BytesIO], str]:
        '''导出为png图片
        args：
            file_name str：设置导出的文件名，如果设置将生成图片文件，否则只返回BytesIO对象
        returns：
            BytesIO：返回文件流对象
        '''
        try:
            flag, data, msg = self.to_html()
            if not flag:
                return flag, data, msg
            tmp_name = "{}.png".format(str(uuid4()))
            tmp_path = os.path.join('/tmp', tmp_name)
            imgkit.from_string(data, tmp_path, options=self.imgkit_options)
            with open(tmp_path, 'rb') as f:
                return True, BytesIO(f.read()), 'ok'
        except Exception as e:
            return False, None, str(e)
        finally:
            if os.path.exists(tmp_path):
                os.remove(tmp_path)

    def to_pdf(self) -> Tuple[bool, Union[None, BytesIO], str]:
        '''导出为pdf文件
        returns：
            BytesIO：返回文件流对象
        '''
        try:
            flag, data, msg = self.to_html()
            if not flag:
                return flag, data, msg
            tmp_name = "{}.pdf".format(str(uuid4()))
            tmp_path = os.path.join('/tmp', tmp_name)
            pdfkit.from_string(data, tmp_path, configuration=self.pdfkit_conf)
            with open(tmp_path, 'rb') as f:
                return True, BytesIO(f.read()), 'ok'
        except Exception as e:
            return False, None, str(e)
        finally:
            if os.path.exists(tmp_path):
                os.remove(tmp_path)
