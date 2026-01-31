# -*- coding: UTF-8 -*-

from request.request import php
from request.status import UpdateStatus
from functional.redis import is_downloading, add_downloading
from functional.files import read_file_to_dict
import time
from common.shell import shell
from service.redis import remote_rc,DOWNLOAD
from common.log import log
from common.ftp import FtpClient
from response.error import invaildJsonFIle
from service.ftp import ConnectFtp
from config import CONFIG
from lib.data import HugoData
import sys
import json

from request.status import UpdateStatus
from handle.loopftp import MainHandle

sys.dont_write_bytecode = True

class ReadJson():
    def __init__(self, hd: HugoData, rc: FtpClient):
        self.hd =hd  # json文件名
        self.hd.resource_ftp.host = CONFIG["ftp_host"]
        self.hd.resource_ftp.port = CONFIG["ftp_port"]
        self.hd.resource_ftp.user = CONFIG["ftp_user"]
        self.hd.resource_ftp.pwd = CONFIG["ftp_pwd"]
        self.hd.resource_ftp.dir = CONFIG["ftp_dir"]
        self.rc = rc
        self.us = UpdateStatus(hd.identifier, hd.user, hd.rule, isupload=hd.isupload)
        self.video_size : int = 0

    
        
    # 检测视频文件小于6G
    def check_video(self, videofile) -> bool:
        
        self.video_size = self.rc.get_size(videofile)
        log.info("size: %d" % self.video_size)
        # if self.video_size == 0:
        #     self.us.fail("视频长度为0")
        #     self.rc.renameappend("-size_is_zero")
        #     return False

        if self.video_size > CONFIG["video_size"] * 1024 * 1024:
            self.us.fail("视频太大超过6G")
            self.rc.renameappend("-video_size_too_large")
            return False
        
        return True

    def _check_rule(self, user: str, rulename: str) -> bool:
        if rulename != "":
            res = php.get_new_rule(user, rulename)
            if res["code"] != 0:
                self.rc.renameappend("-rule_not_found")
            return True
        return True

    def run(self) -> bool:
        exsit = php.exsit_identifier(self.hd.identifier)
        # 下载json文件到本地
        if "video" in dict_conf:
            # us = UpdateStatus(hd.identifier,hd.user, hd.rule)
            if not self._check_rule(self.hd.user, self.hd.rule):
                self.rc.renameappend("-rule_not_found")
                return False
            err, ok = self.hd.check_ftp_integrity()
            if not ok:
                log.error(err)
                self.rc.renameappend(err)
                return False
            # 查看视频文件是否存在
            if not self.rc.exsit(self.hd.filename):
                # 如果没找到文件 第一次报错 改为  没找到-30分钟后重试
                # value = local_rc.get(self.hd.identifier)
                # if not value:
                #     # 第一次
                #     local_rc.set(self.hd.identifier, json.dumps({"retry": 1, "expired":  30*60+int(time.time())}))
                #     return False
                # not_founc_dict = json.loads(value)
                # if not_founc_dict["retry"] == 1 and int(time.time()) > not_founc_dict["expired"]:
                #     # 第二次, 2小时
                #     local_rc.set(self.hd.identifier, json.dumps({"retry": 2, "expired":  120*60+int(time.time())}))
                #     return False
                # # 完了 第二次 改为  没找到-2小时后重试
                # if not_founc_dict["retry"] == 2 and int(time.time()) > not_founc_dict["expired"]:
                #     # 第三次, 6小时
                #     local_rc.set(self.hd.identifier, json.dumps({"retry": 3, "expired":  6*60*60+int(time.time())}))
                #     return False
                # # 第三次 改为  没找到- 6小时后重试
                # if not_founc_dict["retry"] == 3 and int(time.time()) > not_founc_dict["expired"]:
                # # 第三四次, 没找到
                #     local_rc.delete(self.hd.identifier)
                self.rc.renameappend("-video_not_found")
                self.us.fail("没有找到视频文件")
                return False 
                   

            if self.rc.is_uploading(self.hd.filename):
                return False
            
            log.info("send to redis")
            # data = {
            #     "name": self.hd.name,  # json文件名(不包含.json)
            #     "user": self.hd.user,   # 用户
            #     "ftp_user": self.hd.ftp_user,
            #     "filename": self.hd.filename,  # 视频文件
            #     "identifier": self.hd.identifier,   # 唯一标识符
            #     "project": self.hd.project,    # 项目文件夹
            #     "rule": self.hd.rule   # 规则名
            # }
            
            data = self.hd.dict()
            
            # data.set_ftp(CONFIG)
            # print(data)
            member = json.dumps(data)
            
            ok = self.check_video(hd.filename)
            if not ok:
                return False
            # 插入到redis
            try:
                
                remote_rc.sadd(DOWNLOAD, member)
                self.us.processing("等待处理，请勿删除ftp资源", self.video_size)
                add_downloading(hd.name + ".json")
                log.info("insert to redis seccessed ......")
            except Exception as e:
                log.info(e)
                return True

            log.info(
                "-----------------handle {} success-----------".format(localfile))
            return True
        if "image" in dict_conf:
            # 图片
            self.us.file_type = 1
            log.info("is image")
            mh = MainHandle(hd, exsit,self.rc)
            return mh.handle_image()
        return True
# 遍历ftp， 将信息插入redis,  包含(json_filename, video_filename, ftp_dir, cover)
#
#
#  只允许一台服务器开启此服务

if CONFIG["debug"]:
        log.set_out(True)
else:
    log.set_log_name("loop_info.log")


if __name__ == "__main__":
    ftp = ConnectFtp(CONFIG["ftp_host"],CONFIG["ftp_user"],CONFIG["ftp_pwd"],CONFIG["ftp_port"])
    log.info(ftp.ls())
    log.set_disable_alert(True)
    while True:
        ftp.cd("/")
        for directory in ftp.ls("/"):
            log.info("start dirctory")
            if directory[0:1] != "/":
                directory = "/" + directory
            # 遍历FTP的文件目录下一层 不需要递归
            if ftp.cd(directory):
                for file in ftp.ls(directory):
                    if file[len(file)-4:] == "json":
                        # 判断json 是否在下载
                        localfile = file.replace(directory+"/", "")
                        log.info("start read json")
                        # 判断是否在处理， 如果在处理， 那么就跳过
                        if is_downloading(localfile):
                            log.info("%s has been downloading" % localfile)
                            continue
                        rc = FtpClient(localfile, ftp, directory[1:])
                        if not ftp.download(localfile, localfile):
                            log.error("download json file error")
                            shell.remove_all(localfile)
                            continue

                        # 读出json文件内容
                        log.info("read file to dict: {}".format(localfile))
                        try:
                            # 从文件中读取并反序列化成字典
                            dict_conf = read_file_to_dict(localfile)
                        except:
                            # 异常了就修改文件名
                            shell.remove_all(localfile)
                            rc.renameappend(invaildJsonFIle)
                            continue 

                        # 判断是否存在 identifier

                        
                        # dict_conf["user"] = dir[1:]
                        # 通过ftp用户获取本身的用户
                        user = php.get_user_by_ftp_user(directory[1:])
                        if user["code"] != 0:
                            log.error("not found ftp user")
                            continue
                        dict_conf["user"] = user["user"]
                        dict_conf["ftp_user"] = directory[1:]
                        dict_conf["name"] = localfile[:-5]
                       
                        log.info(dict_conf)
                        hd = HugoData(**dict_conf)
                        # 增加判断，不是爬虫的话，规则不能为空
                        if hd.rule == "" and dict_conf["user"] not in CONFIG["spider"]:
                            rc.renameappend("_rule_is_empty")
                        rj = ReadJson(hd, rc)
                        rj.run()
                        shell.remove_all(localfile)
            time.sleep(5)
