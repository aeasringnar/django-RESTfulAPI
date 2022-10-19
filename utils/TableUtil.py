from io import BytesIO
from tempfile import NamedTemporaryFile
from typing import Tuple, Union

from bs4 import BeautifulSoup
from pyecharts.components import Table
from pyecharts.options import ComponentTitleOpts

from utils.HtmlToImgPdfKit import HtmlToImgPdfKit


class TableUtil:
    '''操作表格数据的类，包括二维数组和DataFrame'''

    def __init__(self, table_title: str, headers: list, rows: list) -> None:
        self.table_css_style = ""
        self.table_title = table_title
        self.headers = headers
        self.rows = rows
        self.img_pdf_kit = HtmlToImgPdfKit()

    def to_html(self) -> Tuple[bool, Union[None, str], str]:
        '''处理数据，将数据转为目标html的str内容'''
        try:
            table = Table()
            table.add(headers=self.headers, rows=self.rows)
            table.set_global_opts(
                title_opts=ComponentTitleOpts(title=self.table_title)
            )
            # 创建临时文件
            tmp_file = NamedTemporaryFile()
            # 输出表格到临时文件
            table.render(tmp_file.name)
            # 使用 BeautifulSoup 读取html
            soup = BeautifulSoup(tmp_file.read(), 'html.parser')
            # 修改样式 如果有定制样式的话
            if self.table_css_style:
                for item in soup.find_all('style'):
                    item.string = self.table_css_style
            return True, soup.prettify(), 'ok'
        except Exception as e:
            return False, None, str(e)

    def get_img_or_pdf(self, out_type: str = 'img', out_path: str = '', options: dict = {}) -> Tuple[bool, Union[BytesIO, None], str]:
        flag, data, msg = self.to_html()
        if not flag:
            return flag, data, msg
        if out_type == 'img':
            return self.img_pdf_kit.to_img(data, data_type=2, out_path=out_path, options=options)
        return self.img_pdf_kit.to_pdf(data, data_type=2, out_path=out_path, options=options)


if __name__ == "__main__":
    tu = TableUtil(table_title='test', headers=[
                   'a', 'b'], rows=[[1, 2], [3, 4]])
    tu.get_img_or_pdf(out_path='test.png')
    # tu.get_img_or_pdf(out_type='pdf', out_path='test.pdf')
