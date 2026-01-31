# -*- coding: UTF-8 -*-

"""
resource： 
    一台机器可以开启多个服务
    从redis u5_resource[list]  获取资源并处理, 读取json文件

    1，只生成资源文件， 

    插入redis key: publish_key[List]

    删除本地下载好的 json。 mp4， jpg

"""
from functional.redis import del_downloading, need_delete
from lib.data import HugoData
from pyscs.scs import SCS
import time
import os
from request.status import UpdateStatus
import json
from config import CONFIG
from common.shell import shell
from common.log import log
from handle.resource import Resource
from service.redis import local_rc, remote_rc,RESOURCE,PUBULISH
import sys
from request.request import php

sys.dont_write_bytecode = True

if CONFIG["debug"]:
    log.set_out(True)
# from service.es import es

"""
resource_dir
生成 封面图， 横向和纵向的缩略图，长预览图，到发布目录，  同步到源文件服务器
成功后删除用户目录下的文件
"""

if __name__ == "__main__":
    logname = "resource.log"
    if os.getenv("NAME"):
        logname = os.getenv("NAME") + ".log"
    if not CONFIG["debug"]:
        log.set_log_name(logname)
    scs = SCS()
    log.info("start resource")
    while True:
        # def __init__(self, local_video_file,local_cover_image, ftp_dir, name, dict_conf):
        try:
            # log.debug("..........resource is not hand , you can stop it in 10s .........................................")
            scs.can_stop()
            time.sleep(3)
            
            # log.info("resource is handing , do not ctrl c")
            str_conf = local_rc.lpop(RESOURCE)
            if not str_conf:
                continue
            scs.can_not_stop()
            log.info(str_conf)
            dict_conf = json.loads(str_conf)
            hd = HugoData(**dict_conf)
            log.set_title("identifier: %s" % hd.identifier)
            log.set_name(hd.identifier)
            us = UpdateStatus(hd.identifier,hd.user,hd.rule, isupload=hd.isupload)
            if need_delete(hd.name + ".json"):
                us.stop()
                continue
        except Exception as e:
            # 找不到文件就跳过
            log.info(e)
            continue
        res = Resource(hd)
        res.update_status.processing("正在生成图片")
        ok, retry = res.handle()
        if ok:
            # 如果处理成功
            publish_data = json.dumps(res.flowdata.dict())
            if not local_rc.rpush(PUBULISH, publish_data):
                log.error("insert to redis failed: ")
                if not local_rc.rpush("RESOURCE"):
                    res.update_status("插入redis失败 需要找回数据")
                    continue

            # 成功了 就删除本地下载的资源文件
            res.update_status.processing("生成图片成功")
            # 视频没问题才会重新发布， 又问题重新发布到另外一套规则必定失败
            pool = res.republish()
            if pool != "":
                if not remote_rc.sadd("pool", json.dumps(pool)):
                    log.error("send pool faild")
            log.info("========================   resource handle successed  ======================")
        else:
            # 失败了就删除处理的文件
            res.update_status.fail(res.error_msg)
            log.info(str_conf)
            if retry:
                try:
                    if not local_rc.rpush(RESOURCE, str_conf):
                            log.error("insert to redis failed")
                except Exception as e:
                    log.info(e)
                    log.info("resource need add: " + str_conf)
                    log.info("=================== resource handle failed ===================")
                continue
            # 失败了并且不用重试的， 直接删除
            shell.remove_all(res.source_dir)
            del_downloading(hd.name + ".json")
            if hd.upload_uid > 0:
                php.post_callback(hd.upload_uid, {
                    "identifier": hd.identifier,
                    "rule": hd.rule,
                    "status": 2,
                    "msg": res.error_msg
                })
            
        shell.remove_all(os.path.join(hd.user,  hd.identifier + ".mp4"))
        shell.remove_all(os.path.join(hd.user, hd.identifier + ".json"))
        shell.remove_all(os.path.join(hd.user, hd.identifier + ".jpg"))
