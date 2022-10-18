from curses import echo
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
from tempfile import mkdtemp
from shutil import copyfile
from typing import Union, Tuple, Any
import logging
from enum import Enum


try:
    import imgkit
    import pdfkit
except Exception as e:
    raise ImportError('imgkit pdftkit not found, pelease run pip install imgkit pdfkit')

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


class ImgPdfKit:
    
    IMGKIT_FUC = {
        1 : imgkit.from_file,
        2 : imgkit.from_string,
        3 : imgkit.from_url
    }
    
    def __init__(self, kit_path: Union[str, None] = None, is_debug: bool=False) -> None:
        if kit_path and not os.path.exists(kit_path):
            raise FileNotFoundError('kit_path is not file path or not found file')
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
    
    def to_img(self, data: str, data_type: DataType=DataType.FILE, out_path: str='', options: dict={}) -> Tuple[bool, Union[BytesIO, None], str]:
        img_format = options.get('format', 'jpg')
        self.default_imgkit_options.update(options)
        print(self.default_imgkit_options)
        tmp_file_path = os.path.join(self.tmp_path, f"{uuid4()}.{img_format}")
        if self.debug: print(tmp_file_path)
        try:
            if data_type not in DataType.values():
                raise Exception('this data type not found')
            handle_fuc = self.IMGKIT_FUC[data_type]
            handle_fuc(data, tmp_file_path, options=self.default_imgkit_options, config=self.imgkit_conf)
            if out_path:
                copyfile(tmp_file_path, out_path)
            with open(tmp_file_path, 'rb') as f:
                return True, BytesIO(f.read()), 'ok'
        except Exception as e:
            logging.error(e)
            logging.exception(e)
            return False, None, str(e)
        finally:
            if os.path.exists(tmp_file_path) and not self.debug: os.remove(tmp_file_path)
    
    def to_pdf(self):
        pass
    
    def __del__(self):
        try:
            if os.path.exists(self.tmp_path) and not self.debug: os.removedirs(self.tmp_path)
        except Exception as e:
            logging.error(e)
            logging.exception(e)


if __name__ == "__main__":
    kit = ImgPdfKit(is_debug=True)
    kit.to_img('card.html', DataType.FILE, options={'format': 'png', 'crop-w': '832'})