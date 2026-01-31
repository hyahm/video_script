# encoding=utf-8

from config import CONFIG
# from service.ftp import ftp
import time
from common.log import log
from functional.files import read_file_to_dict
from common.shell import shell
from request.status import UpdateStatus
from common.ffmpeg import ffmpeg
from service.ftp import ConnectFtp
from functional.images import png2jpg
from lib.data import HugoData
from request.request import php
from functional.redis import del_downloading
import os

class Downloader():

    def __init__(self, HugoData: HugoData, ftp: ConnectFtp):
        # "name": hd.name,  # json文件名(不包含.json)
        # "user": hd.user,   # 用户
        # "ftp_user": hd.ftp_user,
        # "filename": hd.filename,  # 视频文件
        # "identifier": hd.identifier,   # 唯一标识符
        # "project": hd.project,    # 项目文件夹
        # "rule": hd.rule   # 规则名
        # 传进来的数据只有 name 和 user 有用， 其他的无视
        self.jsonname = HugoData.name + ".json"
        self.filename = HugoData.filename
        self.project = HugoData.project
        self.project_id = HugoData.project_id
        self.user = HugoData.user
        self.ftp_user = HugoData.ftp_user
        self.name = HugoData.name
        self.flowdata = HugoData
        # 资源服务器的相对目录
        self.reactive = os.path.join(HugoData.project, HugoData.user, self.flowdata.identifier)
        # 资源服务器的根目录
        self.cover = HugoData.user + "/" + self.flowdata.identifier + ".jpg"
        self.video_path = os.path.join(HugoData.user, self.flowdata.identifier + ".mp4")
        self.us = UpdateStatus(self.flowdata.identifier, HugoData.user, self.flowdata.rule, isupload=self.flowdata.isupload)
        self.local_json_file = os.path.join(HugoData.user, self.flowdata.name + ".json")
        self.error = ""
        self.ftp = ftp
        

    def handle(self):
        """
            验证json和转化视频
        
        """
        
        # self.flowdata.category = php.get_alias_name(self.flowdata.video.cat)
        # 下载视频文件
        # 下载json文件
        # name： json 文件名， 不带后缀
        # ftp json 文件路径， 重命名用
        # 下载需要使用的文件, 视频文件和封面图, 剧集封面图
        # 用户目录， 不存在就创建
        shell.makedir(self.flowdata.user)
      
        # 方便返回php  优先下载json 文件
        log.debug("start download json file")
        self.ftp.cd("/" + self.flowdata.ftp_user)
        if not self.ftp.download(self.jsonname, self.local_json_file):
            log.info("download {} error: {}".format(self.jsonname, self.ftp.error()))
            self.us.fail("下载json文件失败")
            self.error = "下载json文件失败"
            # 下载失败的话， 直接删除
            return False
        try:
            log.debug("start read json file to dict")
            jd = read_file_to_dict(self.local_json_file)
            self.flowdata = HugoData(**jd)
            self.flowdata.filename = self.filename
            self.flowdata.project = self.project
            self.flowdata.project_id = self.project_id
            self.flowdata.user = self.user
            self.flowdata.owner = self.user
            self.flowdata.ftp_user = self.ftp_user
            self.flowdata.name = self.name
            # 将 name 和 user 填充到 json 数据中
        except Exception as e:
            log.info(e)
            self.error = "不是标准的json文件"
            self.us.fail("不是标准的json文件")
            return False
        # 下载剧集封面图， 
        log.debug("start download cover")
        # 封面图固定名字
        covername = self.flowdata.identifier + ".jpg"
        coverfield = ""
        self.ftp.cd("/" + self.flowdata.ftp_user)
        if self.ftp.exist(covername):
            # 下载封面图
            if not self.ftp.download(covername, self.cover):
                self.error = "下载失败封面图"
                self.us.fail("下载失败封面图")
                return False
            # 将图片转为jpg
            if not png2jpg(self.cover, self.cover):
                self.us.fail("不支持的图片格式")
            coverfield = self.cover
        else:
            self.us.processing("没有上传封面图，稍后自动生成")
        self.flowdata.postparam.cover = coverfield
        # 下载视频
        log.debug("开始下载视频")
        if not self.download_and_check_video():
            self.error = "视频有问题"
            shell.remove_all(self.local_json_file)
            shell.remove_all(self.cover)
            return False
        return True


    def rename(self, suffix):
        self.ftp.rename(self.jsonname, self.jsonname + suffix)

    def download_and_check_video(self):
        # 下载并检查视频完整性
        
        
        log.debug("start download and to mp4")
        if not self.download_video():
            return False
        # 检查视频
        log.debug("start check video")
        log.info(self.video_path)
        if not ffmpeg.check_video(self.video_path):
            self.us.fail("视频有问题")
            self.rename("-video_have_broken")
            log.info("视频有问题")
            return False
        # 其他类型转成mp4
        return self.to_mp4()
    
    def download_video(self):
        # 下载后转mp4
        start = time.time()
        # 临时文件
        log.info("download... video")
        self.ftp.cd("/" + self.flowdata.ftp_user)
        if not self.ftp.exist(self.flowdata.filename):
            self.us.fail("没有找到视频")
            self.rename("-video_not_found")
            log.info("ftp not found video ")
            return False
        if not self.ftp.download(self.flowdata.filename, self.video_path):
            self.us.fail("视频下载失败")
            log.error("download {} error: {}".format(self.flowdata.filename ,self.ftp.error()))
            return False
        log.info("download video consume: {}".format(time.time()-start))
        log.info(os.stat(self.video_path).st_size)
        return True
        
        
    def to_mp4(self):
        tmp_video_file = "{}.mp4".format(time.time())
        if not self._video_to_mp4(tmp_video_file):
            self.rename("-broken_video")
            shell.remove_all(tmp_video_file)
            return False
        return True

    def cut_mp4(self, vd_code:str, ac_code: str, count: int, tmp_video_file:str):
        ffinfo = ffmpeg.get_json_info(self.video_path)
        # 计算是否存在元数据，如果存在就删掉
        haveMeta = False
        # 计算起始时间是不是从0开始， 如果不是也需要转码
        start = True
        for stream in ffinfo.streams:
            if stream.start_time != "0.000000":
                start = False
            if stream.codec_type == "data":
                haveMeta = True
        if vd_code == "h264" and ac_code == "aac" and start and not haveMeta and count==2:
            return True
        else:
            # 转码为h264，输出到video_dir
            if self.flowdata.after:
                length = int(float(ffinfo.format.duration))
                if not ffmpeg.to_mp4(self.video_path, tmp_video_file, self.flowdata.before, length - self.flowdata.after):
                    self.us.fail("转码为MP4格式失败:{}".format(vd_code))
                    self.rename("-convert_to_mp4_error")
                    return False
            else:
                if not ffmpeg.to_mp4(self.video_path, tmp_video_file):
                    self.us.fail("转码为MP4格式失败:{}".format(vd_code))
                    self.rename("-convert_to_mp4_error")
                    return False
        return True
    
    def _video_to_mp4(self, tmp_video_file):
        log.info("mp4_video_path: %s" % self.video_path)
        # 1.获取视频内部编码
        vd_code, ac_code, count = ffmpeg.get_vcode(self.video_path)
        if not vd_code:
            self.us.fail("视频图像有问题")
            self.rename("-video_vcode_error")
            return False
        if not ac_code:
            self.us.fail("视频声音有问题")
            self.rename("-video_vcode_error")
            return False
        if count <= 1:
            self.us.fail("视频编码缺失")
            self.rename("-video_vcode_error")
            return False
        if not self.cut_mp4(vd_code, ac_code, count, tmp_video_file):
            self.us.fail("转码为MP4格式失败:{}".format(vd_code))
            self.rename("-convert_to_mp4_error")
            return False
            
        if os.path.exists(tmp_video_file):
            log.info("视频转化完成")
            shell.move_to(tmp_video_file, self.video_path)
        # 替换掉老文件
        return True