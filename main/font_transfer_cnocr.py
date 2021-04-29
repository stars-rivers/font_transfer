# -*- coding: utf-8 -*-

"""
@author: caoaoyun
@license: MIT
@file: font_transfer.py
@time: 2021/3/29
@desc: 字体转换ocr版本，将字型分割绘制在不同的图片上一张张的识别（多线程不适用）淘汰
"""
import copy
import threading
import time
from concurrent.futures import ThreadPoolExecutor

import cnocr
import numpy
from PIL import Image, ImageDraw, ImageFont
from fontTools.ttLib import TTFont


class FontTransfer(object):
    _instance_lock = threading.Lock()

    def __init__(self):
        self.font_size = 20  # 字体文字的尺寸
        self.image_size = self.font_size + 4
        self.ocr = cnocr.CnOcr()
        self.res_dict = dict()
        self.thread_pool = ThreadPoolExecutor(15)

    # 线程安全的单例模式
    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, '_instance'):
            with FontTransfer._instance_lock:
                if not hasattr(cls, '_instance'):
                    FontTransfer._instance = super().__new__(cls)

            return FontTransfer._instance

    def get_chars_from_font(self, font_path):
        """
        从字体文件中获取字体编码、字体字型等信息，过滤掉空白的字型编码
        :param font_path: 字体文件路径 str
        :return: dict
        """
        ttf = TTFont(font_path)
        return {k: v for k, v in ttf['cmap'].getBestCmap().items() if ttf['glyf'][v].xMax}

    def draw_font_word(self, char_unicode, font, v):
        """
        在画板上画出字体文件中的字型
        :param char_unicode: unicode编码字符串 str
        :param origin: 字型的位置坐标 list
        :param board: 画板对象
        :param font: 字型对象
        :return: None
        """
        board = Image.new('RGB', (self.image_size, self.image_size), (255, 255, 255))
        draw = ImageDraw.ImageDraw(board)

        # 自适应字型在图片中保持居中
        center_background = (self.image_size / 2, self.image_size / 2)
        size = draw.textsize(char_unicode, font=font)
        origin = [center_background[0] - size[0] / 2, center_background[1] - size[1] / 2]

        draw.text(tuple(origin), char_unicode, font=font, fill=0)

        # board.save(f"./img/{v}.png")
        ndarry = numpy.asarray(board)
        res = self.ocr.ocr_for_single_line(copy.deepcopy(ndarry))
        self.res_dict[v] = res[0] if res else ''

    def font_to_image(self, font_path):
        """
        自适应画出图片的大小，生成字体字型的坐标
        :param font_path:
        :return:
        """
        char_dict = self.get_chars_from_font(font_path)

        font = ImageFont.truetype(font_path, self.font_size)

        for k, v in char_dict.items():
            char_unicode = chr(k)
            self.thread_pool.submit(self.draw_font_word, char_unicode, font, v)

        self.thread_pool.shutdown()
        return self.res_dict


if __name__ == '__main__':
    ft = FontTransfer()
    t = time.time()
    res_dict = ft.font_to_image('../font/land.ttf')
    print('haha', res_dict)
    print(len(res_dict))
    print(time.time() - t)
