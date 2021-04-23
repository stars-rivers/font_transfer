# -*- coding: utf-8 -*-

"""
@author: caoaoyun
@license: MIT
@file: font_transfer.py
@time: 2021/3/29
@desc: 字体转换
"""
import io
import os
import queue
import math
import shutil
import threading
from itertools import chain
import copy
import numpy
from PIL import Image, ImageChops, ImageDraw, ImageFont
from fontTools.ttLib import TTFont
from fontTools.unicode import Unicode

# os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'  # 消除tensorflow的日志输出
# import muggle_ocr
import cnocr
from concurrent.futures import ThreadPoolExecutor


def deepcopy(origin):
    pass


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
        :return: set
        """
        ttf = TTFont(font_path, ignoreDecompileErrors=True)
        chars = chain.from_iterable([y + (Unicode[y[0]],) for y in x.cmap.items()] for x in ttf["cmap"].tables)
        return set(list(chars))

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
        chars = self.get_chars_from_font(font_path)
        # 字体能被分成多少行多少列的正方形图片
        num = math.ceil(math.sqrt(len(chars)))
        # 自适应图片的大小
        image_size = num * (self.font_size + 4)

        font = ImageFont.truetype(font_path, self.font_size)

        unicode_list = []
        board = Image.new('RGB', (image_size, image_size), (255, 255, 255))

        origin = [0, 0]
        i = 1
        j = 1
        thread_pool = ThreadPoolExecutor(15)
        for char in chars:
            origin[0] = 24 * (j - 1) + 2
            origin[1] = 24 * (i - 1) + 2

            if j % num == 0:
                i += 1
                j = 0
            if ImageChops.invert(board).getbbox():
                unicode_list.append(char[1])

            char_unicode = chr(char[0])

            thread_pool.submit(self.draw_font_word, char_unicode, copy.copy(origin), board, font)

            j += 1
        # print(unicode_list)
        # board.save("res.png")
        thread_pool.shutdown()
        return numpy.asarray(board), unicode_list

    # def image_bytes_to_string(self):
    #     while not self.q.empty():
    #         img_name, img_data = self.q.get()
    #
    #         chinese = self.ocr.ocr_for_single_line(self.image_path + img)
    #         self.transfer_dict[img_name] = chinese[0] if chinese else ''
    #
    #         self.q.task_done()

    def get_font_transfer_dict(self, font_path):
        img_array, unicode_list = self.font_to_image(font_path)
        string_list = []
        for res in self.ocr.ocr(img_array):
            string_list += res
        print(unicode_list)
        print(len(unicode_list))
        print(string_list)
        print(len(string_list))
        # return dict(zip(unicode_list, string_list))



