# encoding=utf-8
from lib.base import filed_to_str, filed_to_bool, filed_to_dict

# 图片处理的结构体
class Image():
    def __init__(self, kwargs):
        self.title = filed_to_str(kwargs, "title")
        self.cat = filed_to_str(kwargs, "cat")
        self.subcat = filed_to_str(kwargs, "subcat")
        self.actor = filed_to_str(kwargs,"actor")

class Picture():
    def __init__(self, kwargs):
        self.identifier = filed_to_str(kwargs, "identifier")
        self.filename = filed_to_str(kwargs, "filename")
        self.rule = filed_to_str(kwargs, "rule")
        self.overwrite = filed_to_bool(kwargs,"overwrite")
        self.image = Image(filed_to_dict(kwargs,"image"))