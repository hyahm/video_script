# -*- coding: UTF-8 -*-

"""
下载器， 一台服务器有切只能运行一个此服务
redis key: u5_download 

功能： 查询redis， 下载json， mp4， jpg 文件到本地， 
# 视频转换成mp4， 图片转化成jpg
下载完成后， 插入新key 到redis u5_resource  list
删除ftp 上的数据，
"""
from turtle import down
from lib.data import HugoData
from lib.resource import ResourceServer
from request.request import php
from pyscs.scs import SCS
from remote.shell import remote_shell
from common.shell import shell
from functional.redis import del_downloading
import os
from common.ffmpeg import ffmpeg
import json
from service.redis import local_rc
from common.log import log
import time
from handle.downloader import Downloader
from config import CONFIG
from service.ftp import ConnectFtp
from service.redis import remote_rc, DOWNLOAD,RESOURCE,PUBULISH
import sys
import socket

sys.dont_write_bytecode = True

if CONFIG["debug"]:
    log.set_out(True)

class Loader():
    def __init__(self):
        pass


if __name__ == "__main__":
    
    logname = "download_info.log"
    if os.getenv("NAME"):
        logname = os.getenv("NAME") + ".log"
    if not CONFIG["debug"]:
        log.set_log_name(logname)
    scs = SCS()
    log.info("start download")
    while True:
        scs.can_stop()
        time.sleep(3)
        
        # 源文件下载到对应用户的目录下

        # 检查任务数量
        # 从队列中随意抽取一个下载资源
        json_str = remote_rc.spop(DOWNLOAD)
        if not json_str:
            continue
        scs.can_not_stop()
        dict_conf = json.loads(json_str)
        ddd = HugoData(**dict_conf)
        re_count = local_rc.llen(RESOURCE)
        pu_count = local_rc.llen(PUBULISH)
        if re_count >= CONFIG["cache"] or pu_count >= CONFIG["cache"]:
            # 优化代码， 队列数量任意一个大于设定值，除了shenhe用户， 其他的都不会下载
            # 使队列满了也可以处理 shenhe 用户的数据
            # 如果不是审核就继续下一个
            if ddd.user != "shenhe":
                remote_rc.sadd(DOWNLOAD, json_str)
                continue
        log.info(json_str)
        if ddd.domain != "" and ddd.domain != socket.gethostname():
            remote_rc.sadd(DOWNLOAD, json_str)
            continue
        # if "comefrom" not in dict_conf:
        #     ddd.comefrom = 0
        log.set_title("identifier: %s" % ddd.identifier)
        log.set_name(ddd.identifier)
        log.info(ddd.resource_ftp.__dict__)
        ddd.resource_ftp.dir = ddd.ftp_user
        try:
            ftp = ConnectFtp(**ddd.resource_ftp.__dict__)
        except Exception as e:
            log.error(e)
            del_downloading(ddd.name + ".json")
            continue
        downloader = Downloader(ddd, ftp)
        
        time.sleep(2)
        downloader.us.processing("正在下载")
        downloader.flowdata.owner = downloader.flowdata.user
        if downloader.handle():
            # 如果规则是空的， 那么将其添加到审核列表中
            # download里面爬虫的的直接上资源
            # 加入到审核列表的条件， script_status = 2, user = "shenhe"
            # todo: 后面会将配置移动到后台配置
            if downloader.flowdata.user in CONFIG["spider"]:
                rs = ResourceServer(**php.get_resource())
                if not rs:
                    log.error("not found resource server info")
                log.info(rs.__dict__)
                localfile = os.path.join(downloader.flowdata.user, downloader.flowdata.identifier)
                downloader.flowdata.postparam.cover = rs.domain + "/" + localfile + ".jpg"

                ffmpeg.get_cover(localfile + ".mp4", 0,localfile + ".jpg")

                resource_root = os.path.join(rs.root, ddd.project, ddd.user, downloader.flowdata.identifier)
                remote_shell.make_remote_dirs(resource_root, rs.ip)
                if not remote_shell.rsync_to_resource(localfile + ".jpg", resource_root, "", rs.ip):
                    log.warning("send image to resource server error")
                if not remote_shell.rsync_to_resource(localfile + ".mp4", resource_root, "", rs.ip):
                    log.error("send video to resource server error")
                    if not remote_rc.sadd(DOWNLOAD, json_str):
                        log.info("redis error")
                    ftp.close()
                    del_downloading(ddd.name + ".json")
                    continue
                downloader.flowdata.postparam.play_url = rs.domain + "/" + localfile + ".mp4"

                downloader.flowdata.postparam.cover = rs.domain + "/" + localfile + ".jpg"
                log.info("start store backend server")
                os.remove(os.path.join(downloader.user,
                          downloader.flowdata.identifier + ".mp4"))
                os.remove(os.path.join(downloader.user, downloader.name + ".json"))
                # 设置需要审核
                # downloader.us.audit(rs.id)
                downloader.flowdata.isspider = True
                downloader.flowdata.status = 2
                # 爬虫需要切一张封面图

                # 删除视频
                log.info("提取封面图完成............")
                # 爬虫直接入公共池， 但是有个问题
                downloader.flowdata.pool = True
                downloader.flowdata.resource = rs
                if downloader.flowdata.video.title == "":
                    downloader.flowdata.video.title = ddd.identifier
                # downloader.flowdata.owner = "shenhe"
                # downloader.flowdata.user = "yingzheng"
                # # ddd.video.cat = ddd.category
                # downloader.flowdata.rule = "yingzheng"
                # remote_rc.sadd("pool", json.dumps(downloader.flowdata.dict()))
                del_downloading(ddd.name + ".json")
            else:
                # 普通用户的丢到resource 进行处理
                log.info("send to resource")
                # downloader.flowdata.category = php.get_alias_name(
                #     downloader.flowdata.video.cat)
                flow = downloader.flowdata.dict()
                log.info(flow)
                if not local_rc.rpush(RESOURCE, json.dumps(flow)):
                    if not remote_rc.sadd(DOWNLOAD, json_str):
                        log.info("redis error")
                        ftp.close()
                        continue
                downloader.us.processing("下载完成")
               
            # 第二步骤完成的话，  基本问题不大了     数据保存至后台
            log.info(downloader.flowdata.owner)
            if not CONFIG["debug"]:
                try:
                    ftp = ConnectFtp(**ddd.resource_ftp.__dict__)
                except Exception as e:
                    log.error(e)
                    del_downloading(ddd.name + ".json")
                    continue
                ftp.cd("/" + downloader.ftp_user)
                if not ftp.delete(downloader.flowdata.filename):
                    log.info("删除失败")
                if not ftp.delete(downloader.name + ".json"):
                    log.info("删除失败")
                ftp.delete(downloader.flowdata.identifier + ".jpg")
            if not php.save_to_resource(downloader.flowdata.dict()):
                try:
                    remote_rc.sadd(DOWNLOAD, json_str)
                except Exception as e:
                    log.error(e)
                    ftp.close()
                    continue
            
            log.info(
                "download seccessed ===========================================")
        else:
            if ddd.upload_uid > 0:
                # 返回错误给第三方上传
                php.post_callback(ddd.upload_uid, {
                    "identifier": ddd.identifier,
                    "rule": ddd.rule,
                    "status": 2,
                    "msg": downloader.error
                })
            # downloader.delete_resouece(dict_conf["identifier"])
            del_downloading(ddd.name + ".json")
            # 失败来就放弃
            # try:
            #     remote_rc.sadd(DOWNLOAD, json_str)
            # except Exception as e:
            #     log.error(e)
            shell.remove_all(downloader.local_json_file)
            shell.remove_all(downloader.video_path)
            shell.remove_all(downloader.cover)
        ftp.close()