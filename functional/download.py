# -*- coding: UTF-8 -*-

import requests
from common.log import log


def overtime():
    """
    超时后的callback函数
    :return: pass
    """
    pass

def download_video(file_url, file_path):
    """
    获取视频资源，限时300秒（5分钟）
    :param file_url: 视频文件的url链接
    :param file_path:  视频文件的保存路径
    :return: bool
    """
    try:
        r = requests.get(file_url, stream=True, timeout=5)
        with open(file_path, "wb") as file:
            file.write(r.content)

    except Exception as e:
        log.info(e)
        return False
    return True



def download_file(file_url, file_path):
    """
    获取图片，片头资源，限时10秒
    :param file_url: 资源文件的url链接
    :param file_path: 资源文件的保存路径
    :return: bool
    """

    try:
        response = requests.get(file_url, stream=True, timeout=30)
        if response.status_code != 200:
            return False
        with open(file_path, "wb") as file:
            file.write(response.content)
    except Exception as e:
        if len(e.args) > 0:
                log.error("[Status]: %s获取失败: %s" % (file_path, str(e.args[0])))
        else:
            log.error("[Status]: %s获取失败: %s" % (file_path, str(e)))
        
        return False
    return True
