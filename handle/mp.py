# encoding=utf-8

from request.request import ReqPHP
from common.log import log
from common.shell import shell
from os import path
from remote.shell import remote_shell
from config import CONFIG, php_ip
import time
from functional.encrypt import encrpyt_from_file
from functional.images import resize_image
from functional.download import download_file
from common.imagelib import ImageHandle
from functional.check import check_date
from lib.newrule import Rule
from lib.serverinfo import get_server_info


# 生成图片, 加密图片


class MakePicture(ReqPHP) :

    def __init__(self, reactive, rule: Rule, filename):
        self.reactive = reactive
        self.rule = rule
        self.filename = filename
        self._temp_filename = ""
        self._cover = ""
        self.source_dir = path.normpath(path.join(path.normpath(CONFIG["local_dir"]) , reactive)) 
        super().__init__()

    def get_image_position(self, position, width, height, logo_width, logo_height):
        # position	int	水印位置 0左上角，1右上角，2左下角，3右下角
        if position == 1:
            return (width-logo_width, 0)
        elif position == 2:
            return (0, height-logo_height)
        elif position == 3:
            return (width-logo_width, height-logo_height)
        else:
            return (0, 0)

    def clean(self):
        shell.remove_all(self._temp_filename)


    def get_font_position(self, position, width, height, size, text):
        # content_postion	int	飘屏水印设置 滚动的位置 1顶部滚动，2中心显示，3底部滚动
        # 显示在屏幕中间， 假设文字的长度为 size * 4/3 * length
        # size * 4//3:  这个文字大小对应的像素
        # 长度假如是 文字的一半
        length = len(text)//2
        font_lenth = size * 4//3 * length
        mid_start = (width - font_lenth)/2
        if position == 2:
            return (mid_start, (height - size * 4//3)/2)
        elif position == 3:
            return (mid_start, (height - size))
        else:
            return (mid_start, 0)
    

    def _add_water(self):
        # self.filename 原图片
        ih = ImageHandle(self.filename)
        log.info(self.rule)
        self._temp_filename = str(time.time()) + "." + str(ih.format).lower()
        create = False
        if self.rule.logo.enable and self.rule.logo.image_url != "":
            create = True
            # 图片水印启用
            # 获取图片文件
            image_file = self.get_filename_from_url(self.rule.logo.image_url)

            download_file(php_ip + self.rule.logo.image_url, image_file)
            # 重新计算 logo的 像素大小
            width = resize_image(image_file, image_file, ih.height, self.rule.logo.scale)
            if not width:
                return False
            # 获取水印的位置
            image_position = self.get_image_position(self.rule.logo.position, ih.width, ih.height, width, ih.height//self.rule.logo.scale)
            log.info("water-----------" + self.rule.logo.image_url)
            if not ih.paste_image(image_file, image_position, dst=self._temp_filename):
                log.error("water failed")
                return False
        if self.rule.font.enable and self.rule.font.text != "":
            create = True
            # 将文字的内容写入到文件
            font_position = self.get_font_position(self.rule.font.position, ih.width, ih.height, self.rule.font.size, self.rule.font.text)
            if not ih.paste_font(dst=self._temp_filename, text=self.rule.font.text,
                        position=font_position,size=self.rule.font.size,color=self.rule.font.color):
                return False

        if not create:
            import shutil
            shutil.copyfile(self.filename, self._temp_filename)
                    
        return True
    
    
    def get_cover(self):
        return self._cover
        
    def encrpyt_pictrue(self, cat):
        # position	int	水印位置 1左上角，2右上角，3左下角，4右下角
        # content_postion	int	飘屏水印设置 滚动的位置 1顶部滚动，2中心显示，3底部滚动
        
        if not self._add_water():
            log.error("add water failed")
            return False
        
        if not encrpyt_from_file(self._temp_filename, self.filename):
            log.error("encrypt image failed")
            return False
        log.info("图片加密完成")
        
        # 生成url并拷贝文件到服务器

        info =  get_server_info(cat)
        if not info:
            return False
        log.info(info)
        if info.cover_path:
            prefix, middle, ok = check_date(info.cover_path)
            if not ok:
                log.error("路径格式不对")
                return False
            # 封面图
            remote_dir = path.join(prefix, middle, self.reactive )
            remote_shell.make_remote_dirs(remote_dir, server=info.host)
            if not remote_shell.rsync_to_server(self.filename, remote_dir , server=info.host):
                log.error("send to publish server error")
                return False
            if middle == "":
                self._cover = "{}/{}/".format(info.cover_url, self.reactive)
            else:
                self._cover = "{}/{}/{}/".format(info.cover_url,middle, self.reactive)
      
        # 请求接口发送数据，然后就完事了
       
        return True

    def get_filename_from_url(self, url: str) -> str:
        start = url.rindex("/")
        if start < 0:
            return ""
        return url[start+1:]
