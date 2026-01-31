# encoding=utf-8

from functional.redis import del_downloading, need_delete
from request.request import php
from service.redis import local_rc,PUBULISH
from request.status import UpdateStatus
import json
from common.log import log
from pyscs.scs import SCS
from app.publish.main import Publish
from config import CONFIG
from common.shell import shell
import os
import time
from lib.data import HugoData
import sys
sys.dont_write_bytecode = True

if CONFIG["debug"]:
    log.set_out(True)

"""
publish： 
    一台机器可以开启多个服务
    接受redis， 

    2, 打水印， 缩略图， 发布到api接口, 读出json 数据后就用不到了， 删掉
    完成后， 删除处理完的资源文件
通过原始文件继续打水印生成到 发布目录
<====>  为了加速处理， 这里也可以来一刀
如果规则需要切割m3u8文件， 切割出m3u8文件
<====> 为避免因第三方接口问题导致循环处理复杂的视频处理，这里需要来一刀分割成2个脚本
拷贝至资源机器并发布给第三方, 
更新对应的json数据
<====>（这里需要来一刀分割成2个脚本） todo: rsync 有缺陷，拷贝文件的时候数据不对， 后面需要优化
如果符合77xxx 用户的视频， 需要单独生成一次16:9 的大长图，后台生成新数据， 更新json 并发布给 77xxx的接口
更新对应的json数据
成功后删除发布目录
"""

if __name__ == "__main__":

    logname = "publish.log"
    if not CONFIG["debug"] and os.getenv("NAME"):
        logname = os.getenv("NAME") + ".log"

        log.set_log_name(logname)
    scs = SCS()
    log.info("start publish")
    # 创建规则目录
    while True:
        dict_conf = None
        try:
            scs.can_stop()
            # log.debug("..........publish is not doing , you can stop it in 10s .........................................")
            time.sleep(3)
            
            str_conf = local_rc.lpop(PUBULISH)
            if not str_conf:
                # 如果队列里面没找到就去后补里面找
                str_conf = local_rc.lpop("backup")
                if not str_conf:
                    continue
            scs.can_not_stop()
            log.info(str_conf)
            dict_conf = json.loads(str_conf)
            hd = HugoData(**dict_conf)
            log.set_title("identifier: %s" % hd.identifier)
            log.set_name(hd.identifier)
            us = UpdateStatus(hd.identifier, hd.user, hd.rule, isupload=hd.isupload)
            if need_delete(hd.name + ".json"):
                us.stop()
                continue
        except Exception as e:
            log.info(e)
            continue

        source_dir = os.path.join(os.path.normpath(
            CONFIG["local_dir"]), hd.project, hd.user, hd.identifier)
        # 判断视频文件是否存在， 不存在就不处理这个了, 正常是肯定存在的
        if not os.path.exists(os.path.join(source_dir, hd.identifier + ".mp4")):
            log.info("not found video file: %s" %
                     os.path.join(source_dir, hd.identifier + ".mp4"))
            continue

        publish = Publish(hd)
        # 是否删除所有
        ok, retry = publish.handle()
        if ok:
            if retry:
                continue
             # 成功了就删除所有资源文件
            if hd.upload_uid > 0:
                php.post_callback(hd.upload_uid, {
                    "identifier": hd.identifier,
                    "rule": hd.rule,
                    "status": 1,
                    "msg": "审核成功"
                })

            del_downloading(publish.flowdata.name + ".json")
            publish.clean()
        else:
            if retry:
                try:
                    local_rc.rpush("backup", json.dumps(publish.flowdata.dict()))
                except Exception as e:
                    log.error(e)
            else:
                if hd.upload_uid > 0:
                    php.post_callback(hd.upload_uid, {
                        "identifier": hd.identifier,
                        "rule": hd.rule,
                        "status": 2,
                        "msg": "审核失败"
                    })
                del_downloading(publish.flowdata.name + ".json")
                publish.clean()
        # 删除规则资源
        if publish.mvh is not None:
            publish.mvh.clean()
        log.info(
            "....................... %s all has complate ............................." % hd.identifier)
