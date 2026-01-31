# -*- coding: UTF-8 -*-

import os
from common.log import log
from config import CONFIG

def check_version():
    """
    检查要3.7以上的版本
    :return: bool
    """
    out = os.popen("python3 --version")

    out_list = out.readlines()[0].replace("\n", "").split(" ")

    version = out_list[1].split(".")
    if int(version[0]) >= 3 and int(version[1]) >= 7:
        return True
    return False



def check_path(name, dst):
    """
    检查web路径，防止输入[..]
    :param name: 文件名
    :param dst: 目标目录
    :return: 验证后的路径
    """
    rec_path = os.path.join(os.path.normpath(dst) , name)
    abs_path = os.path.abspath(rec_path)
    verify = abs_path[:len(dst)] == dst
    return verify

def check_date(path):
    # 传路径进来， 
    # 服务器路径如果有时间就获取时间路径
    # 返回时间包含后面的
    import datetime
    now = datetime.datetime.now().strftime('%Y%m%d')
    count = path.count(CONFIG["date"]) 
    if count > 1:
        log.error("路径格式不对")
        return path, "", False
    if count == 0:
        return path, "", True
    i = path.index(CONFIG["date"])
    return path[:i], path[i:].replace(CONFIG["date"], now, 1), True