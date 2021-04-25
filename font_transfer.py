# -*- coding: utf-8 -*-

"""
@author: caoaoyun
@license: MIT
@file: font_transfer.py
@time: 2021/3/29
@desc: 字体转换
"""
import copy
import math
import threading
from concurrent.futures import ThreadPoolExecutor

import cnocr
import numpy
from PIL import Image, ImageDraw, ImageFont
from fontTools.ttLib import TTFont


class FontTransfer(object):
    _instance_lock = threading.Lock()

    def __init__(self):
        self.font_size = 20  # 字体文字的尺寸
        self.ocr = cnocr.CnOcr()
        self.transfer_dict = dict()

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

        char_dict = {}
        for k, v in ttf['cmap'].getBestCmap().items():
            if ttf['glyf'][v].xMin:
                char_dict[k] = v
        return char_dict

    def draw_font_word(self, char_unicode, origin, board, font):
        """
        在画板上画出字体文件中的字型
        :param char_unicode: unicode编码字符串 str
        :param origin: 字型的位置坐标 list
        :param board: 画板对象
        :param font: 字型对象
        :return: None
        """
        draw = ImageDraw.ImageDraw(board)
        draw.text(tuple(origin), char_unicode, font=font, fill=0)

    def font_to_image(self, font_path):
        """
        自适应画出图片的大小，生成字体字型的坐标
        :param font_path:
        :return:
        """
        char_dict = self.get_chars_from_font(font_path)
        # 字体能被分成多少行多少列的正方形图片
        num = math.ceil(math.sqrt(len(char_dict)))
        # 自适应图片的大小
        image_size = num * (self.font_size + 4)

        font = ImageFont.truetype(font_path, self.font_size)

        unicode_list = list(char_dict.values())
        board = Image.new('RGB', (image_size, image_size), (255, 255, 255))

        # 这个算法用于确定每个字型的坐标
        origin = [0, 0]
        i = 1
        j = 1
        thread_pool = ThreadPoolExecutor(15)
        for k in char_dict.keys():
            origin[0] = 24 * (j - 1) + 2
            origin[1] = 24 * (i - 1) + 2

            if j % num == 0:
                i += 1
                j = 0

            char_unicode = chr(k)

            thread_pool.submit(self.draw_font_word, char_unicode, copy.copy(origin), board, font)

            j += 1
        # print(unicode_list)
        # board.save("res.png")
        thread_pool.shutdown()
        return numpy.asarray(board), unicode_list

    def get_font_transfer_dict(self, font_path):
        img_array, unicode_list = self.font_to_image(font_path)
        string_list = []
        for res in self.ocr.ocr(img_array):
            string_list += res
        return dict(zip(unicode_list, string_list))
