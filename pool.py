# encoding=utf-8

# 遍历公共池，功能类似downloader， 但是不需要验证
from lib.data import HugoData
import os
import json
from request.status import UpdateStatus
from request.request import php
import time
from functional.files import create_dir
from functional.redis import add_downloading, is_downloading, need_delete
from config import CONFIG
from pyscs.scs import SCS
from common.log import log
from service.redis import remote_rc, local_rc,RESOURCE,PUBULISH

from remote.shell import remote_shell
import sys
from common.ffmpeg import ffmpeg

sys.dont_write_bytecode = True

"""
再次切片， 审核通过(上传审核不会进来) 会到这里来， 功能类似download， 但是没有download 复杂

"""


if __name__ == "__main__":
    # 下载2个文件到本地， 封面图和视频
    # 旋转后覆盖本地和资源文件

    #     {
    #   "identifier": "fffff",
    #   "video": {
    #     "title": "fffffffffff",
    #     "cat": "mm_手机下载",
    #     "subcat": "变态另类,成人动漫",
    #     "actor": "ddddddd"
    #   },
    #   "filename": "dongman4.mp4",
    #   "rule": "请问请问",
    #   "overwrite": true,
    #   "name": "fffff"
    # }

    log.set_log_name("pool.log")
    scs = SCS()
    log.info("start pool")
    while True:
        scs.can_stop()
        time.sleep(3)
        scs.can_not_stop()
        # 源文件下载到对应用户的目录下
        # 得到的就是完整的json， 不需要
        # 检查任务数量
        try:
            re_count = local_rc.llen(RESOURCE)
            pu_count = local_rc.llen(PUBULISH)
            # 队列数量任意一个大于设定值，都不会下载
            if re_count >= CONFIG["cache"] or pu_count >= CONFIG["cache"]:
                continue
        except Exception as e:
            log.info(e)
            continue
        try:
            json_str = remote_rc.spop("pool")
            
            if not json_str:
                continue
            dict_conf = json.loads(json_str)
            log.info(json_str)
            hd = HugoData(**dict_conf)
            log.set_title("identifier: %s" % hd.identifier)
            log.set_name(hd.identifier)
            if hd.video.cat == "":
                log.info("没有分类信息")
                continue
            if is_downloading(hd.name + ".json"):
                # 正在处理就跳过
                log.info("is downloading ")
                continue
        except Exception as e:
            log.info(e)
            continue
        us = UpdateStatus(hd.identifier, hd.user, hd.rule, isupload=hd.isupload)
        if need_delete(hd.name + ".json"):
            us.stop()
            continue
        create_dir(hd.user)
        owner = dict_conf["owner"]
        # 源文件的project。 todo: 
        if not php.get_project_by_cat_and_subcat(hd.video.cat, hd.video.subcat, owner):
            log.info("cat or subcat error")
            continue
        # cat = dict_conf["category"]
        # log.info(cat)
        # if owner == "shenhe":
        #     user = "shenhe"
        local_cover_filename = os.path.join(hd.user, hd.identifier + ".jpg")
        local_video_filename = os.path.join(hd.user, hd.identifier + ".mp4")
        reactive = os.path.join(hd.resource.root, hd.project, owner, hd.identifier)
        # 从owner中下载视频
        if not remote_shell.download_from_resource(os.path.join(reactive,  hd.identifier+".mp4"), local_video_filename,hd.resource.ip):
            us.fail("download mp4 failed")
            log.info("download mp4 failed")
            continue
        ffinfo = ffmpeg.get_json_info(local_video_filename)
        # 计算是否存在元数据，如果存在就删掉
        haveMeta = False
        # 计算起始时间是不是从0开始， 如果不是也需要转码
        start = True
        for stream in ffinfo.streams:
            if stream.start_time != "0.000000":
                start = False
            if stream.codec_type == "data":
                haveMeta = True
        if not start or haveMeta:
            # 转码为h264，输出到video_dir
            if not ffmpeg.to_mp4(local_video_filename, local_video_filename):
                continue
            remote_shell.rsync_to_resource(local_video_filename, reactive,  hd.identifier+".mp4",hd.resource.ip)
        mp4file = os.path.join(dict_conf["user"], dict_conf["identifier"]+".mp4")

        # 下载封面图
        ok = remote_shell.download_from_resource(os.path.join(reactive,  hd.identifier+".jpg"), local_cover_filename,hd.resource.ip)
        # log.error("download mp4 failed")
        # remote_rc.sadd("pool",json_str)
        log.info(json.dumps(hd.dict()))
        if not local_rc.rpush(RESOURCE, json.dumps(hd.dict())):
            us.fail("redis 插入失败")
            log.info("redis 插入失败")
            continue
        add_downloading(hd.name + ".json")
        # 提示当先下载完成
        
        if not php.save_to_resource(hd.dict()):
            us.fail("下载完成， 但是更新失败, 请手动操作")
            log.info("下载完成， 但是更新失败")
            continue
        log.info("download seccessed.......")
