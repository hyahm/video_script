# encoding=utf-8

# 遍历公共池，功能类似downloader， 但是不需要验证
import os
import json
from request.status import UpdateStatus
from common.ffmpeg import ffmpeg
import time
from functional.redis import is_downloading, del_downloading
from config import CONFIG
from pyscs.scs import SCS
from remote.shell import remote_shell
from common.log import log
from service.redis import remote_rc
from common.shell import shell
import sys
sys.dont_write_bytecode = True


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
    #   "identifier": "fffff"
    # }

    log.set_log_name("rotate.log")
    scs = SCS()
    log.info("start resource")
    while True:
        scs.can_stop()
        time.sleep(3)
        scs.can_not_stop()
        # 源文件下载到对应用户的目录下
        # 得到的就是完整的json， 不需要
        # 检查任务数量
        try:
            json_str = remote_rc.spop("rotate")

            if not json_str:
                continue
            log.info(json_str)
            dict_conf = json.loads(json_str)
            
            if is_downloading(dict_conf["name"] + ".json"):
                # 正在处理就跳过
                log.info("is downloading ")
                continue
        except Exception as e:
            log.info(e)
            del_downloading(dict_conf["name"] +
                            ".json")
            continue
        # 通过json获取mp4和cover
        if "isupload" not in dict_conf:
            dict_conf["isupload"] = False
        us = UpdateStatus(dict_conf["identifier"], dict_conf["user"],
                          dict_conf["rule"], isupload=dict_conf["isupload"])
        # 修改状态， 提示正在旋转
        us.rotate("正在旋转视频")
        log.set_title("identifier: %s" % dict_conf["identifier"])
        log.set_name( dict_conf["identifier"])
        # 下载视频
        if dict_conf["user"] == "shenhe" and dict_conf["category"] == "77crawl":
            dict_conf["category"] = ""
        if not shell.download_from_resource(
                dict_conf["identifier"],  dict_conf["identifier"]+".mp4", dict_conf["user"], ""):
            log.info("download mp4 failed")
            # remote_rc.sadd("rotate", json_str)
            us.rotate("无法处理")
            del_downloading(dict_conf["name"] +".json")
            continue

        # 旋转视频

        temp = str(time.time()) + ".mp4"
        if dict_conf["rotate"] == 0:
            if not ffmpeg.rotate90(dict_conf["identifier"]+".mp4", temp):
                shell.remove_all(temp)
                us.rotate("视频有问题")
                del_downloading(dict_conf["name"] + ".json")
                continue
        elif dict_conf["rotate"] == 1:
            if not ffmpeg.rotate180(dict_conf["identifier"]+".mp4", temp):
                shell.remove_all(temp)
                us.rotate("视频有问题")
                del_downloading(dict_conf["name"] + ".json")
                continue
        elif dict_conf["rotate"] == 2:
            if not ffmpeg.rotate270(dict_conf["identifier"]+".mp4", temp):
                shell.remove_all(temp)
                us.rotate("视频有问题")
                del_downloading(dict_conf["name"] + ".json")
                continue
        else:
            continue
        shell.move_to(temp, dict_conf["identifier"]+".mp4")
        remote = os.path.join(CONFIG["resource_dir"],  dict_conf["user"],
                              dict_conf["category"], dict_conf["identifier"], dict_conf["identifier"]+".mp4")
        if not remote_shell.rsync_to_server(dict_conf["identifier"]+".mp4", remote):
            log.info("download mp4 failed")
            remote_rc.sadd("rotate", json_str)
            continue

        # 修改状态， 提示旋转完成
        us.audit()
        del_downloading(dict_conf["name"] + ".json")
