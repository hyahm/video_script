# -*- coding: UTF-8 -*-

import os
from common.ftp import FtpClient
from common.shell import shell
from common.log import log
from lib.newrule import get_rule
from lib.data import HugoData
from handle.mp import MakePicture
from functional.files import have_space
from request.third import Third
from functional.images import get_format
from request.request import php
from request.status import UpdateStatus


# 主处理类
# 只下载json文件， 判断json文件内容合法性, 图片处理的
class MainHandle(Third):
    """
    从ftp下载数据，存到redis
    output to redis: 
    data = {
            "ftp_dir": self.ftp_dir,
            "name": self.name,
            "user": self.user,
            "filename": self.dict_conf["filename"],
            "identifier": self.dict_conf["identifier"],
            "category": self.category,
            "rule": self.dict_conf["rule"]
        }
    """

    def __init__(self, dict_conf: HugoData, exsit: bool, ftp: FtpClient):
        # 项目目录保存的json 文件， 临时的
        self.ftp_dir = '/' + dict_conf.ftp_user
        self.jsonfile = dict_conf.name + ".json"
        self.dict_conf = dict_conf
        self.user = dict_conf.user
        # 不带后缀的文件名, ftp上json， 视频， 图片 共用的
        self.name = dict_conf.name
        self.exsit = exsit
        # ftp 目录
        self.ftp = ftp
        self.rule = dict_conf.rule
        # 不带后缀的文件名, ftp上json， 视频， 图片 共用的
        super().__init__(dict_conf.identifier, dict_conf.user, dict_conf.rule, False)
        self.us = UpdateStatus(
            dict_conf.identifier, dict_conf.user, dict_conf.rule, file_type=1)

    def _get_rule(self):
        if self.dict_conf.rule != "":
            self.rule = get_rule(self.user, self.dict_conf.rule)
            if not self.rule:
                return False
        return True

    def handle_image(self):
        
        log.info("start cut image")
        if not self.check_image_field():
            if self.exsit:
                self.us.fail(self.error_name)
            self.ftp.rename(self.jsonfile, self.jsonfile.replace(
                ".json", self.error_name))
            return False
        
        self.ftp.cd("/" + self.ftp_dir)
        failed = 0
        # 这里下载规则
        log.info("检查image完成")
        # 遍历所有图片, 找到identifier-   后缀是jpg的文件
        images = self.ftp.ls(self.ftp_dir)
        log.info(images)
        if len(images) == 0 and self.exsit:
            self.us.fail("没有发现一张要处理的图片")
            return False
        self.dict_conf.postparam.thumb_series = []
        rule = get_rule(self.user, self.rule, 1)
        if not rule:
            log.info("获取规则失败")
            return False
        success = 0
        reactive = os.path.join(self.dict_conf.project, self.dict_conf.user, self.dict_conf.identifier)
        log.info("for images")
        for ftpfile in images:
            # ftpfile 是完整路径, 去掉前面的 /dir/   剩下的f 就是文件名
            f = ftpfile.replace(self.ftp_dir + "/", "")
            log.info(f)
            log.info(self.dict_conf.identifier)
            # 如果文件名的前面与identifier相等， 那么可能是需要处理的图片文件
            if self.dict_conf.identifier == f[:len(self.dict_conf.identifier)]:
                d = f.rindex(".")
                # 找到想关图片
                if f[d:] in [".jpg", ".jpeg", ".png"]:
                    # 下载文件
                    log.info("download img")
                    if not self.ftp.download(f, f):
                        log.info("下载图片失败")
                        if self.exsit:
                            self.us.fail("下载图片失败")
                        return False
                    #  避免非 png 或 jpeg 的图片冒充， 直接跳过
                    suffix = get_format(f)
                    if suffix not in ["jpeg", "png"]:
                        failed += 1
                        log.info("not jpeg or png img")
                        if self.exsit:
                            self.us.fail("not jpeg or png img")
                        continue
                    # 直接改为正确的后缀名
                    self.dict_conf.filename = f[:d] + "." + suffix
                    log.info("start add picture")
                    # 修改为正确的后缀名
                    shell.move_to(f, self.dict_conf.filename)
                    log.info(self.dict_conf.filename)
                    # 图片加水印                    
                    mp = MakePicture(reactive, rule, self.dict_conf.filename )
                    # 1 是图片规则
                    
                    # 图片加密
                    if mp.encrpyt_pictrue(self.dict_conf.image.cat):
                        self.dict_conf.postparam.thumb_series.append(
                            self.dict_conf.filename )
                        log.info(self.dict_conf.filename )
                        log.info(self.dict_conf.postparam.thumb_series)
                        
                        # 处理成功就删除图片文件
                        self.ftp.delete(f)
                        success = success + 1
                    else:
                        log.info("加密失败")
                        # 里面任何一个失败就跳过
                        failed += 1
                        mp.clean()
                        continue
                        # 删除资源
                    mp.clean()
                    self.dict_conf.postparam.cover = mp.get_cover()
                    # 删除加密文件
        
        # 有处理成功的， 但是有处理失败的， 才继续
        log.info("成功 %d 个" % success)
        if success > 0:
            log.info(self.jsonfile)
            # 所有图片文件处理完成才能删除json文件
        
            self.us.success("处理失败, 个数: {}".format(failed))
            self.ftp.delete(self.jsonfile)
            # 保存到本地
            log.info(self.dict_conf.dict())
            if not self.save_image_to_resource(self.dict_conf.dict()):
                if self.exsit:
                    self.us.fail("请求接口失败")
                return False

            self.us.success("图片处理完成")
        if success == 0 and failed == 0:
            log.info("not found any match prefix is identifier of image file")
            pass
            # shell.remove_all(self.dict_conf["filename"])
        return True

    # def check_ftp_integrity(self):
    #     if not self._get_rule():
    #         return False
    #     # 判断文件是否合法， 再检查内容
    #     if not self.check_space(self.jsonfile):
    #         self.ftp.rename(self.jsonfile, self.jsonfile.replace(
    #             ".json", self.error_name))
    #         return False
    #     if "image" in self.dict_conf:
    #         self.handle_image()
    #         # delete_resouece()
    #         return False
    #     elif "video" in self.dict_conf:
    #         log.info("check video")
    #         return self.handle_video()
    #     else:
    #         self.us.fail("json字段错误")
    #         return False
    #     return True

    # def handle_video(self):
    #     log.info("check json file")
    #     if not self.check():
    #         self.ftp.rename(self.jsonfile, self.jsonfile.replace(
    #             ".json", self.error_name))
    #         log.info("check failed")
    #         return False
    #     # 检查ftp视频
    #     log.info("检查ftp视频")
    #     if not self.check_ftp_video():
    #         log.info("检查视频错误")
    #         return False

    #     log.info("send to redis")
    #     log.info(self.dict_conf)
    #     data = {
    #         "name": self.name,  # json文件名
    #         "user": self.user,   # 用户
    #         "filename": self.dict_conf["filename"],  # 视频文件
    #         "identifier": self.dict_conf["identifier"],   # 唯一标识符
    #         "rule": self.dict_conf["rule"]   # 规则名
    #     }

    #     member = json.dumps(data)

    #     # 插入到redis
    #     try:
    #         remote_rc.sadd(DOWNLOADING, member)
    #         self.us.processing("等待处理，请勿删除ftp资源")
    #         log.info("insert to redis seccessed ......")
    #     except Exception as e:
    #         log.info("filename %s not add to redis" %
    #                  self.dict_conf["name"] + ".json")
    #         self.us.fail("插入redis 失败")
    #         return False

    #     return True

    # def check_ftp_video(self):
    #     if not self.check_video_suffix():
    #         self.us.fail("视频格式不支持")
    #         self.ftp.rename(self.jsonfile, self.jsonfile.replace(
    #             ".json", ".json-not_found_video_file"))
    #         return
    #     # ftp 上检查视频
    #     self.ftp.cd(self.ftp_dir)
    #     if not self.ftp.exist(self.dict_conf["filename"]):
    #         # 要判断有没有封面图， 如果有就只处理封面图，
    #         self.us.fail("没有找到视频文件")

    #         self.ftp.rename(self.jsonfile, self.jsonfile.replace(
    #             ".json", ".json-not_found_video_file"))

    #         log.error("not_found_video_file")
    #         return False

    #     # 检测视频文件小于6G
    #     video_size = self.ftp.getsize(self.dict_conf["filename"])
    #     log.info("size: %d" % video_size)
    #     if video_size == 0:
    #         self.us.fail("视频文件大小0")
    #         self.ftp.rename(self.jsonfile, self.jsonfile.replace(
    #             ".json", ".json-video_size_is_zero"))
    #         log.error("video_size_is_zero")
    #         return False

    #     if video_size > CONFIG["video_size"] * 1024 * 1024:
    #         self.us.fail("视频文件太大")
    #         self.ftp.rename(self.jsonfile, self.jsonfile.replace(
    #             ".json", ".json-video_size_too_large"))
    #         return False

    #     if self.ftp.is_uploading(self.dict_conf["filename"]):
    #         log.info("文件正在下载.....")
    #         return False
    #     return True

    # def check(self):
    #     # 检查视频
    #     if not self.check_json():
    #         return False
    #     log.info("check check_video_field")
    #     if not self.check_video_field():
    #         return False
    #     log.info("check rule")
    #     # rule不为空才检查分类
    #     if self.dict_conf["rule"]:
    #         if not self.dict_conf.get("overwrite", False):
    #             if not self.check_title_and_identifier(self.dict_conf):
    #                 self.error_name = self.get_error_name()
    #                 return False
    #     if not self.check_video_suffix():
    #         return False
    #     return True

    # def check_json(self):
    #     keys = ["identifier", "filename"]
    #     for k in keys:
    #         if not self.dict_conf.get(k, False):
    #             self.us.fail("缺少字段: {}".format(k))
    #             self.error_name = ".json-error_{}_is_empty".format(k)
    #             return False
    #     return True

    # def check_video_suffix(self):
    #     sl = self.dict_conf["filename"].split(".")
    #     suffix = sl[-1]
    #     if suffix not in CONFIG["valid_video_types"]:
    #         self.us.fail("视频格式不支持")
    #         self.error_name = ".json-valid_video_types"
    #         return False
    #     return True

    # def check_video_field(self):
    #     # video
    #     keys = ["title", "cat", "subcat"]
    #     for k in keys:
    #         if not self.dict_conf["video"].get(k, False):
    #             self.us.fail("video缺少字段: {}".format(k))
    #             self.error_name = ".json-valid_video_types"
    #             return False

    #     # 检查本地分类
    #     self.category = self.check_cate_and_subcat(
    #         self.dict_conf["video"]["cat"], self.dict_conf["video"]["subcat"].split(","))
    #     if not self.category:
    #         self.us.fail("本地分类没找到")
    #         log.error("not found cat int database")
    #         self.error_name = ".json-error_not_found_cat_in_database"
    #         return False

    #     # 接口的分类
    #     return True

    # 检查 video 里面的字段
    def check_image_field(self):
        # video
        log.info("check field")
        keys = ["title", "cat"]
        for k in keys:
            if not self.dict_conf.image:
                log.info("image field")
                if self.exsit:
                    self.us.fail("image缺少字段: {}".format(k))
                self.error_name = ".json-valid_image_types"
                return False

        # 检查本地分类
        if not self.check_cate_and_subcat():
            log.info("本地分类没找到")
            if self.exsit:
                self.us.fail("本地分类没找到")
            self.error_name = ".json-error_not_found_cat_in_database"
            return False

        # 接口的分类
        return True

    def check_space(self, jsonfile):
        # 检查json， identify， mp4 文件是否有空格
        names = [jsonfile, self.dict_conf["identifier"],
                 self.dict_conf["filename"]]
        field = ["json_file", "identifier", "filename"]
        for i, _ in enumerate(names):
            if have_space(names[i]):
                if self.exsit:
                    self.us.fail("字段{}有空格".format(field[i]))
                self.error_name = ".json--error_{}_have_space".format(field[i])
                return False
        return True

    def check_cate_and_subcat(self) -> bool:
        if not self.dict_conf.image.cat or not self.dict_conf.image.subcat:
            return False
        return php.get_project_by_cat_and_subcat(self.dict_conf.image.cat, self.dict_conf.image.subcat, self.dict_conf.user)
        # log.info(category)
        # if catename in category:
        #     scmap = {}
        #     log.info(category[catename]["subcat"])
        #     for x in category[catename]["subcat"]:
        #         scmap[x] = 0
        #     for sc in subcat:
        #         if sc not in scmap:
        #             return False

        #     return category[catename]["alias_name"]

        # return False
