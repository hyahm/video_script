# encoding=utf-8
from common.ffmpeg import ffmpeg
from common.log import log
from os.path import join
from common.shell import shell
from functional.download import download_file
from lib.newrule import Rule
from request.request import php
import time

class MakeVideoHLS():
    """
        生成 hls 和 生成动态图
    """

    def __init__(self, video_path: str, resource_dir: str, rule: Rule, user: str):
        """
        video_path: 视频路径
        resource_dir: 资源根目录
        rule: 规则
        user: 所属用户
        """
        self.video_path = video_path
        self.temp_name = str(time.time()) + "_encrypt.txt"
        self.resource_dir = resource_dir
        self.rule = rule
        self.user = user
        self.key_file = ""

    def clean(self):
        shell.remove_all(self.temp_name)


    def get_encrypt_file(self) -> bool:
        res = php.get_encrype(self.user)
        if res["code"] != 0:
            log.error("get key error")
            return False
        encryptdata = res["data"]
        index = encryptdata["key_url"].rindex("/")
        self.key_file = encryptdata["key_url"][index+1:]
        # 判断文件是否存在， 存在就不用下载
        # if not exists(key_file):
            
            # 这里必定成功，如果不成功无限重试
        if not download_file(encryptdata["key_url"], self.key_file):
            log.error("download key file error")
            time.sleep(1)
            return False

        # 直接复制key 文件到 m3u8文件的同一级目录， 看打开的目录位置来移动
        
        with open(self.temp_name, "w+", encoding="utf-8") as f:
            # 这里如果也改了，那么就是
            f.write(self.key_file + "\n")
            # f.write(encryptdata["key_url"] + "\n")
            f.write(self.key_file + "\n")
            f.write(encryptdata["iv"])
        return True

    def make_hls(self, this_curr=1) -> bool:
        """
        this_curr: hls下级目录, 基本就是第几集的,用来区分不同的m3u8
        """
        # 生成ts 文件， 放入到output 下面。 output 规则： <source>/indentified/<filename>/hls/episode/xxx.ts
        # encrypt.txt 格式 3行， 第一行是key.txt的url, 第二行是key.txt 本地的文件路径， 第三行是iv， 随机的32位字符串、
        # key.txt 生成命令  openssl rand 16 > key.txt
        # iv 生成：  openssl rand -hex 16
        # 测试 m3u8   http://stream-tester.jwplayer.com/
        # 创建hls
        # 操作的根目录
       
        hls_root = join(self.resource_dir, "hls/{}/".format(this_curr))
        output = join(hls_root, "index.m3u8")
        try:
            shell.makedir(hls_root)
        except Exception as e:
            log.error(e)

        shell.copy(self.key_file, join(hls_root, self.key_file))
        # log.info(key_file + "\n" + key_file + "\n" + encryptdata["iv"])
        if not ffmpeg.make_encrypt_tls_77xxx(self.video_path, output, self.temp_name,
                                                self.rule.m3u8.interval, self.rule.m3u8.bitrate, self.rule.m3u8.fps):
            log.error("make hls failed")
            shell.remove_all(self.temp_name)
            return False
        return True