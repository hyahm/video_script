# -*- coding: UTF-8 -*-

import os
from codecs import BOM_UTF8
import json
import re
from common.log import log


def create_dir(folder):
    """
    若目录不存在则创建
    :param folder:目录路径
    :return:
    """
    log.info("create folder %s" % folder)
    if os.path.exists(folder):
        # 存在
        if os.path.isfile(folder):
            raise Exception("%s is a file" & folder)
        
    else:
        # 没权限会raise
        try:
            os.makedirs(folder, mode=0o755, exist_ok=True)
        except:
            raise Exception("%s Permission Access" & folder)

def split_file(filename):
    """
    分离文件名和后缀
    :param filename:文件名称（非路径）
    :return:
    """
    dotindex = filename.rindex(".")
    basename = filename[:dotindex]
    extension = filename[dotindex + 1:]
    return basename, extension

def print_json(dicts):
    if isinstance(dicts, (dict, list)):
        log.info(json.dumps(dicts,indent=4))
        return
    if isinstance(dicts, str):
        try:
            log.info(json.dumps(json.loads(dicts), indent=4))
            return
        except:
            pass
    log.error("not supports")

def read_file_to_dict(file):
    try:
        return json.loads(lstrip_bom(open(file, 'r', encoding="utf-8").read()))
    except Exception as e:
        raise Exception(e)

def lstrip_bom(str_):
    # s = str_.decode("utf-8")
    bom_str = BOM_UTF8.decode("utf-8")
    if str_.startswith(bom_str):
        return str_[len(bom_str):]
    else:
        return str_

def is_letter(self, name):
    letter = re.compile("^(?!\d+$)[\da-zA-Z_-]+$")     #数字和字母组合，不允许纯数字
    # FIRST_LETTER = re.compile("^[a-zA-Z]")     #只能母开头
    if letter.search(name):
        # if FIRST_LETTER.search(name):
        return True
    return False

# 数组子集
def arr_is_in(sub, par):
    """
    sub  子集
    par： 父级
    return: bool
    """
    for v in sub:
        v = v.strip()
        if v in par:
            continue
        else:
            return False
    return True


def have_space(s):
    if not s:
        return True
    pattern = re.compile ("\\s", re.S)
    return bool(pattern.findall(s))

def getmd5(file):
    import hashlib
    m = hashlib.md5()
    with open(file,'rb') as f:
        for line in f:
            m.update(line)
    md5code = m.hexdigest()
    return md5code

