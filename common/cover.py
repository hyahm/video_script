# encoding=utf8

from os import path
import os
from common.imagelib import ImageHandle
from functional.images import resize_image
from config import CONFIG
from request.request import php
from common.shell import shell
from common.log import log
from common.ffmpeg import ffmpeg


class Cover:
    # 封面图只是切割横纵封面图
    def __init__(self, cover, epi_cover, dst, identifier, dict_conf):
        """
        cover： cover 路径
        epi_cover： epi_cover  路径
        dst: 生成最终目标目录
        name： json 文件名
        dict_conf： json 文件解析后的dict
        """
        if not dict_conf:
            raise Exception("no dict_conf")
        self.dict = dict_conf
        self.cover = cover
        self.epi_cover = epi_cover
        self.dst_path = path.normpath(dst)
        shell.makedir(self.dst_path)
        self.identifier = identifier
        # 根据分类名来创建文件夹
        self.dir = dict_conf["category"]
    
    def set_user(self, user):
        self.dict["user"] = user

    def cut(self):
        # 切割封面图， 修改后的dict
        if self.cover != "":
            self.thumb(self.cover, "cover")
            shell.move_to(self.cover, self.dst_path)
        if self.epi_cover != "":
            self.thumb(self.epi_cover)
            shell.move_to(self.epi_cover, self.dst_path)
        return self.dict

    
       
    def thumb(self, image_file, suffix=""):
        """
        缩略图必须存在， 不然raise
        """
        # thumb_hor  310*174 横向的缩略图
        # thumb_ver 纵向的缩略图 180*246
        if suffix != "":
            suffix = "_" + suffix
        try:

            ih = ImageHandle(image_file)
        except Exception as e:
            log.error(e)
            return False
        # 通过封面获取横向缩略图
        if not ih.get_thumb(path.join(self.dst_path, self.identifier +  suffix + "_hor.jpg"), 310, 174):
            return False
        # 通过封面获取纵向缩略图
        if not ih.get_thumb(path.join(self.dst_path, self.identifier +  suffix +"_ver.jpg"), 180, 246):
            return False

        # 通过封面获取大横向缩略图
        if not ih.get_thumb(path.join(self.dst_path, self.identifier +  suffix +"_hor_large.jpg"), 310*5, 174*5):
            return False
        # 通过封面获取大纵向缩略图
        if not ih.get_thumb(path.join(self.dst_path, self.identifier +  suffix +"_ver_large.jpg"), 180*5, 246*5):
            return False

    
    def add_water(self, water_image="water.png"):
        # 打水印前的文件肯定是 mp4
        video_path = os.path.join(self.dst_path, self.identifier + ".mp4") 
        # 获取高度， 用来计算水印的图大小
        _, height = ffmpeg.get_video_shape(video_path)
        if not height:
            return False
        # 高度1/8
        log.info("开始打水印======================")
        tmp_video = os.path.join(self.dst_path, "tmp_" + self.identifier + ".mp4")
        # 临时生成的水印图片
        tmp_water_image = self.identifier + water_image
        if not resize_image(water_image, tmp_water_image, height):
            log.error("create water image failed")
            return False
        log.info("tmp_image : %s" % tmp_water_image)
        if not ffmpeg.u5_to_480_left(video_path, tmp_video, tmp_water_image):
            shell.remove_all(tmp_water_image)
            log.info("water failed...........")
            return False
        
        shell.move_to(tmp_video, video_path)
        
        shell.remove_all(tmp_water_image)
        
        return True