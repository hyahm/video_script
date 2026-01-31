'''
@Author: your name
@Date: 2020-03-02 09:50:44
LastEditTime: 2022-02-06 12:52:50
LastEditors: Please set LastEditors
@Description: In User Settings Edit
@FilePath: /u5/asset/images.py
'''
# -*- coding: UTF-8 -*-

import os
from PIL import Image, ImageFile
from common.log import log
import tempfile


def png2jpg(src, dst):
    try:
        log.debug(src)
        img = Image.open(src)
        log.debug(img.format)
        if img.format == "JPEG":
            return True
        if img.format == "PNG":
            bg = Image.new("RGB", img.size, (255, 255, 255))
            bg.paste(img)
            bg.save(dst)
            return True
        else:
            log.error("不支持的图片格式")
            return False
    except Exception as e:
        log.error(e)
        return False


def get_image_shape(imagefile):
    try:
        image = Image.open(imagefile)
        return image.size
    except:
        return 0, 0


def produce_image(file_in, file_out):
    """
    转换输入图片的像素比例
    :param file_in:输入图片路径
    :param file_out:输出图片路径
    :return:none
    """
    image = Image.open(file_in)
    multiple = round(image.height / 100)
    width = round(image.width / multiple)
    height = round(image.height / multiple)
    resized_image = image.resize((width, height), Image.ANTIALIAS)
    try:
        ImageFile.MAXBLOCK = width * height
        resized_image.save(file_out)
    except Exception as e:
        log.error(e)
        return False
    return True


def make_long_preview(images_path, output):
    """
    制作长预览图
    :param images_path:由图片所在目录路径拼接的临时目录路径，临时目录已切割出100张截图   合并后的像素不能超过 65500
    :return bool
    """
    # 临时目录((
    images_path = os.path.normpath(images_path)
    output = os.path.normpath(output)
    log.info(os.listdir(images_path))
    try:
        images = [Image.open(os.path.join(images_path, fn)) for fn in os.listdir(images_path) if
                  fn.endswith('.jpg')]
        # 获取size
        width, height = images[0].size
        new_canvas = Image.new(images[0].mode, (width * len(images), height))
        count = 0
        tempfile.SpooledTemporaryFile = tempfile.TemporaryFile
        log.info(width)
        ImageFile.MAXBLOCK = width * height * len(images)
        for img in images:
            resize = img.resize((width, height))
            new_canvas.paste(resize, (width * count, 0))
            count += 1

        new_canvas.save(output)
    except Exception as e:
        log.error(e)
        return False
    return True


def make_long_preview_to_size(images_path:str, w: int, h: int, output: str) -> bool:
    """
        制作自定义宽高的长预览图
        :param images_path:由图片所在目录路径拼接的临时目录路径，临时目录已切割出100张截图   合并后的像素不能超过 65500
        :return bool
        """
    # 临时目录((
    images_path = os.path.normpath(images_path)
    output = os.path.normpath(output)
    try:
        lenth = len(os.listdir(images_path))
        new_canvas = Image.new("RGB", (w * lenth, h))
        for i in range(1, lenth+1):
            im = Image.open(os.path.join(images_path, "tmp{}.jpg".format(i)))
            new_canvas.paste(im, (w * i, 0))
        new_canvas.save(output)
    except Exception as e:
        log.error(e)
        return False
    return True


def resize_image(input: str, output: str, height: int, scale=15)->int:
    """
    转换输入图片的像素比例
    :param height: 视频高度
    :param scale:  缩小15倍
    :return: width  返回新图片的宽度

    """
    try:
        if scale == 0:
            scale = 15
        log.info(input)
        image = Image.open(input)
        this_width, this_height = image.size
        new_height = height // scale
        new_width = new_height * this_width // this_height
        resized_image = image.resize((new_width, new_height), Image.ANTIALIAS)
        resized_image.save(output)
    except Exception as e:
        log.error(e)
    return new_width





def get_format(input):
    try:
        log.info(input)
        image = Image.open(input)
        return image.format.lower()
    except Exception as e:
        log.error(e)
        return ""


def cut(input: str, output: str, cut_width: int, cut_height: int):
    image = Image.open(input)
    background_image = Image.new('RGB', (cut_width, cut_height), (0, 0, 0))
    width, height = image.size
    # to_heigth = height * width // 640
    if width * cut_height >= height * cut_width:
        # 依照此宽度进行缩放图片
        new_width = cut_width
        new_heigth = height * new_width // width

    else:
        new_heigth = cut_height
        new_width = width * new_heigth // height

    new_image = image.resize((new_width, new_heigth), Image.ANTIALIAS)
    # new_image.show()
    # if w == 0:
    #     background_image.paste(new_image, (0, (height - h) // 2))
    # else:
    background_image.paste(new_image, ((cut_width - new_width) // 2, 0))
    # background_image.show()
    background_image = background_image.convert("RGB")
    background_image.save(output)


def to_webp(image_path, out):
    # 图片转为webp
    try:
        im = Image.open(image_path).convert("RGB")
        im.save(out, "WEBP")
        return True
    except:
        return False
