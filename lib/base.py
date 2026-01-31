# encoding=utf-8

from typing import Dict
import json

def filed_to_int(base:Dict, field:str, default: int = 0) -> int: 
    """
        只支持str转换
        base: dict   元数据
        field: 字段
        default: 默认值
        
    """
    if not isinstance(base, dict):
        return default
    src = base.get(field, default)
    if isinstance(src, float):
        res = int(src)
        if src == 0:
            return default
        return res
    if isinstance(src, int):
        if src == 0:
            return default
        return src
    if isinstance(src, str):
        try:
            src = int(src)
            if src == 0:
                return default
        except:
            pass
    return default

def filed_to_str(base:Dict, field:str, default: str = "") -> str: 
    """
        只支持str转换
        base: dict   元数据
        field: 字段
        default: 默认值
        
    """
    if not isinstance(base, dict):
        return default
    src = base.get(field, default)
    
    if isinstance(src, bool):
        if src:
            return "true"
        else:
            return "false"
    if isinstance(src, float):
        return str(src)
    if isinstance(src, int):
        return str(src)
    if isinstance(src, str):
        if src == "":
            return default
        return src
    return default

def filed_to_bool(base:Dict, field:str, default: bool=False) -> bool: 
    """
        只支持str转换
        base: dict   元数据
        field: 字段
        default: 默认值
        
    """
    if not isinstance(base, dict):
        return default
    src = base.get(field, default)
    if isinstance(src, bool):
        return src
    if isinstance(src, int):
        return src != 0
    if isinstance(src, str):
        if src.lower() == "true":
            return True
        if src.lower() == "false":
            return False
        try:
            intsrc = int(src)
            return intsrc != 0
        except:
            pass
    return default


def filed_to_dict(base:Dict, field:str, default: dict = {}) -> dict: 
    """
        只支持str转换
        base: dict   元数据
        field: 字段
        default: 默认值
        
    """
    if not isinstance(base, dict):
        return default
    src = base.get(field, default)
    if isinstance(src, dict):
        return src
    if isinstance(src, str):
        try:
            res = json.loads(src)
            return res
        except:
            pass
    return default

    

def filed_to_list(base:Dict, field:str, default: list = []) -> list: 
    """
        只支持str转换
        base: dict   元数据
        field: 字段
        default: 默认值
        
    """
    if not isinstance(base, dict):
        return default
    src = base.get(field, default)
    if isinstance(src, list):
        if src == []:
            return default
        return src
    if isinstance(src, str):
        try:
            res = json.loads(src)
            if isinstance(res, list):
                if res == []:
                    return default
                return res 
        except:
            pass
    return default