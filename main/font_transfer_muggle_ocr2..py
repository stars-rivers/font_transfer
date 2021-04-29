# -*- coding: utf-8 -*-

"""
@author: caoaoyun
@license: MIT
@file: font_transfer.py
@time: 2021/3/29
@desc: 字体转换muggle-ocr版本，将n个字型绘制在m张图片上，对m张图片进行识别，速度提升了17%，但可能导致数据错位
"""
import io
import math
import os
import threading
import time
from concurrent.futures import ThreadPoolExecutor

os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'
import muggle_ocr
from PIL import Image, ImageDraw, ImageFont
from fontTools.ttLib import TTFont


class FontTransfer(object):
    _instance_lock = threading.Lock()

    def __init__(self):
        self.font_size = 20  # 字体文字的尺寸
        self.image_size = self.font_size + 4
        self.ocr = muggle_ocr.SDK(model_type=muggle_ocr.ModelType.OCR)
        self.res_dict = dict()
        self.line_num = 5  # 每一行识别的字数

    # 线程安全的单例模式
    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, '_instance'):
            with FontTransfer._instance_lock:
                if not hasattr(cls, '_instance'):
                    FontTransfer._instance = super().__new__(cls)

            return FontTransfer._instance

    def get_chars_from_font(self, font_path):
        """
        从字体文件中获取字体编码、字体字型等信息
        :param font_path: 字体文件路径 str
        :return: dict
        """
        ttf = TTFont(font_path)
        return {k: v for k, v in ttf['cmap'].getBestCmap().items() if ttf['glyf'][v].xMax}

    def draw_font_word(self, char_unicode, font, draw, origin):
        """
        在画板上画出字体文件中的字型
        :param char_unicode: unicode编码字符串 str
        :param origin: 字型的位置坐标 list
        :param board: 画板对象
        :param font: 字型对象
        :return: None
        """
        draw.text(tuple(origin), char_unicode, font=font, fill=255)

    def font_to_image(self, font, char_dict):
        """
        自适应画出图片的大小，生成字体字型的坐标
        :param font_path:
        :return:
        """
        thread_pool = ThreadPoolExecutor(self.line_num)
        board = Image.new('RGB', (self.image_size * self.line_num, self.image_size), (0, 0, 0))
        char_list = []
        for ids, v in enumerate(char_dict.items()):
            draw = ImageDraw.ImageDraw(board)
            char_unicode = chr(v[0])
            center_background = (self.image_size / 2, self.image_size / 2)
            size = draw.textsize(char_unicode, font=font)
            origin = [center_background[0] - size[0] / 2 + ids * self.image_size, center_background[1] - size[1] / 2]
            thread_pool.submit(self.draw_font_word, char_unicode, font, draw, origin)
            char_list.append(v[1])
        thread_pool.shutdown()
        img_byte = io.BytesIO()
        board.save(img_byte, format='PNG')
        img_data = img_byte.getvalue()
        result = self.ocr.predict(img_data)
        if len(char_list) == len(result):
            for k, v in zip(char_list, result):
                self.res_dict[k] = v

    def crop_char_dict(self, font_path):
        char_dict = self.get_chars_from_font(font_path)
        font = ImageFont.truetype(font_path, self.font_size)
        thread_pool = ThreadPoolExecutor(math.ceil(len(char_dict) / self.line_num))
        for i in range(math.ceil(len(char_dict) / self.line_num)):
            small_dict = dict()
            for _ in range(self.line_num):
                if char_dict:
                    k, v = char_dict.popitem()
                    small_dict[k] = v
            # self.font_to_image(font, small_dict)
            thread_pool.submit(self.font_to_image, font, small_dict)
            # print(small_dict)
        thread_pool.shutdown()

        print(self.res_dict)
        print(len(self.res_dict))


if __name__ == '__main__':
    ft = FontTransfer()
    t = time.time()
    ft.crop_char_dict('../font/land.ttf')
    print(time.time() - t)
