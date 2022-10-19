import logging
import os
import time
from enum import Enum
from io import BytesIO
from shutil import copy
from tempfile import mkdtemp
from typing import Any, Tuple, Union
from uuid import uuid4

try:
    import imgkit
    import pdfkit
except Exception as e:
    raise ImportError(
        'imgkit pdftkit not found, pelease run pip install imgkit pdfkit')


class DataType(int, Enum):
    FILE = 1
    STRING = 2
    URL = 3

    @classmethod
    def keys(cls) -> set:
        return set(cls.__members__.keys())

    @classmethod
    def values(cls) -> list:
        return list(cls.__members__.values())


class HtmlToImgPdfKit:

    IMGKIT_FUC = {
        1: imgkit.from_file,
        2: imgkit.from_string,
        3: imgkit.from_url
    }

    PDFKIT_FUC = {
        1: pdfkit.from_file,
        2: pdfkit.from_string,
        3: pdfkit.from_url
    }

    def __init__(self, kit_path: Union[str, None] = None, is_debug: bool = False) -> None:
        if kit_path and not os.path.exists(kit_path):
            raise FileNotFoundError(
                'kit_path is not file path or not found file')
        self.imgkit_conf = imgkit.config(
            wkhtmltoimage=kit_path) if kit_path else None
        self.pdfkit_conf = pdfkit.configuration(
            wkhtmltopdf=kit_path) if kit_path else None
        self.default_imgkit_options = {
            'format': 'jpg',
            # 'crop-w': '832', # set image weight
            'crop-y': '0',
            'crop-x': '0',
            'encoding': "UTF-8",
        }
        # options doc https://wkhtmltopdf.org/usage/wkhtmltopdf.txt
        self.default_pdfkit_options = {
            "encoding": "UTF-8",
            # 'margin-top': '0',
            # 'margin-right': '0', # Set the page right margin (default 10mm)
            # 'margin-bottom': '0',
            # 'margin-left': '0', # Set the page left margin (default 10mm)
        }
        self.debug = is_debug
        self.tmp_path = mkdtemp()

    def to_img(self, data: str, data_type: DataType = DataType.FILE, out_path: str = '', options: dict = {}) -> Tuple[bool, Union[BytesIO, None], str]:
        '''将HTML生成为图像的方法
        args：
            data str：传入的数据，可以是文件路径、文本内容、URL，必填。
            data_type int：传入的数据类型，可选值为 1 文件地址 2 文本内容 3 URL，必填
            out_path str：传入的输出地址，选填。
            options dict：传入选项字典，用于设置生成图片的格式，选填。
        returns：
            (bool, BytesIO/None, str)：返回成功标识、文件流/None、异常描述
        '''
        img_format = options.get(
            'format', 'jpg') if 'format' in options else self.default_imgkit_options.get('format')
        out_path = f"{os.path.splitext(out_path)[0]}.{img_format}"
        self.default_imgkit_options.update(options)
        tmp_file_path = os.path.join(self.tmp_path, f"{uuid4()}.{img_format}")
        if self.debug:
            print(tmp_file_path)
        try:
            if data_type not in DataType.values():
                raise Exception('this data type not found')
            handle_fuc = self.IMGKIT_FUC[data_type]
            handle_fuc(data, tmp_file_path,
                       options=self.default_imgkit_options, config=self.imgkit_conf)
            if out_path:
                copy(tmp_file_path, out_path)
            with open(tmp_file_path, 'rb') as f:
                return True, BytesIO(f.read()), 'ok'
        except Exception as e:
            logging.error(e)
            logging.exception(e)
            return False, None, str(e)
        finally:
            if os.path.exists(tmp_file_path) and not self.debug:
                os.remove(tmp_file_path)

    def to_pdf(self, data: str, data_type: DataType = DataType.FILE, out_path: str = '', options: dict = {}) -> Tuple[bool, Union[BytesIO, None], str]:
        '''将HTML生成为PDF的方法
        args：
            data str：传入的数据，可以是文件路径、文本内容、URL，必填。
            data_type int：传入的数据类型，可选值为 1 文件地址 2 文本内容 3 URL，必填
            out_path str：传入的输出地址，选填。
            options dict：传入选项字典，用于设置生成PDF的格式，选填。
        returns：
            (bool, BytesIO/None, str)：返回成功标识、文件流/None、异常描述
        '''
        self.default_pdfkit_options.update(options)
        tmp_file_path = os.path.join(self.tmp_path, f"{uuid4()}.pdf")
        if self.debug:
            print(tmp_file_path)
        try:
            if data_type not in DataType.values():
                raise Exception('this data type not found')
            handle_fuc = self.PDFKIT_FUC[data_type]
            handle_fuc(data, tmp_file_path, options=self.default_pdfkit_options,
                       configuration=self.pdfkit_conf)
            if out_path:
                copy(tmp_file_path, out_path)
            with open(tmp_file_path, 'rb') as f:
                return True, BytesIO(f.read()), 'ok'
        except Exception as e:
            logging.error(e)
            logging.exception(e)
            return False, None, str(e)
        finally:
            if os.path.exists(tmp_file_path) and not self.debug:
                os.remove(tmp_file_path)

    def __del__(self):
        try:
            if os.path.exists(self.tmp_path) and not self.debug:
                os.removedirs(self.tmp_path)
        except Exception as e:
            logging.error(e)
            logging.exception(e)


if __name__ == "__main__":
    kit = HtmlToImgPdfKit()
    kit.to_img('card.html', DataType.FILE, options={
               'crop-w': '526'}, out_path='current.jpg')
    kit.to_pdf('card.html', DataType.FILE, out_path='current.pdf')
