# encoding=utf-8
from service.ftp import ftp
from functional.images import png2jpg
from common.log import log
from request.status import UpdateStatus


class Cover():

    def __init__(self, cover_path: str):
        self._cover_path = cover_path
        self._suffix = ""

    def get_cover(self) -> str:
        return self._cover_path

    def get_suffix(self) -> str:
        return self._suffix

    def download_cover(self, identifier, ftp_dir, user, rule, isupload) -> bool:
        us = UpdateStatus(identifier, user, rule, isupload=isupload)
        suffixs = ["jpg", "png", "jpeg"]
        for suffix in suffixs:
            log.debug("check {}".format(suffix))
            covername = identifier + "." + suffix
            ftp.cd("/" + ftp_dir)
            if ftp.exist(covername):
                if ftp.download(covername, self._cover_path):
                    log.debug("start transform cover")
                    if not png2jpg(self._cover_path,self._cover_path):
                        self._suffix = ".json-not_support_image_format"
                        us.fail("不支持的图片格式")
                        return False
                    return True
                # log.error("download cover failed")
                us.fail("下载失败封面图")
                return False
            log.info("not found cover image")
        us.processing("没有上传封面图，稍后自动生成")
        self._cover_path = ""
        return True