# encoding=utf-8
from pydantic import BaseModel, ValidationError, validator, validate_arguments,root_validator
from lib.newrule import Rule, get_rule
from app.publish.webp import MakeVideoWebp
data =   {"code":0,"data":{"font":{"enable":True,"text":"本视频由9UU视频网络收集 海外永久访问地址 www.9uu.com 大陆访问域名 www.cchz77.com","color":"#FFFFFF","size":25,"position":0,"interval":380,"scroll":25,"border":0,"shadow":False,"space":30},"webp":{"enable":True,"start":60,"interval":0,"count":5},"logo":{"enable":True,"image_url":"/mysource/images/20201027134935_111.png","position":0,"padding":35,"scale":8},"m3u8":{"encrypt":False,"enable":True,"interval":2,"bitrate":0,"fps":0},"head":{"enable":False,"video_url":""},"ad":{"enable":True,"url":"/image/1654831252738181557/1654831252738181557.png","start":10,"stay":0},"before":0,"after":0,"api_path":"https://krv26.com/callback/hugoCallback","resolve":2,"image_format":0},"count":0,"index":0}
rule = Rule(**data["data"])
print(rule.font)
mvw = MakeVideoWebp("tmpvideo", "C:\\Users\\cande\\Desktop\\436b44e3bb7809d76df11ab69d4e43e8.mp4", rule.webp, 20, 20, 1000)
mvw.make_webp()
# class UserModel(BaseModel):
#     name: int = 0

#     @root_validator( pre=True)
#     def name_must_contain_space(cls, v):
#         if isinstance(v, int):
#             return 0
#         return v
#         # if v == "":
#         #     return "aaaa"
#         #     # raise ValueError('must contain a space')
#         # return v.title()

# um = UserModel(**{"name": "aaa"})
# print(um.name)