# -*- coding: UTF-8 -*-

import redis
from config import CONFIG

# 排队到download
DOWNLOAD="u5_download"
# 正在处理的
DOWNLOADING="u5_downloading"
# 从正在处理中删除
DELETE = "hugo_delete"
# 排队到resource
RESOURCE="u5_resource"
# 排队到publish
PUBULISH="u5_publish"

class Redis(object):
    def __init__(self, kargs):
        self.kargs = kargs
        self.r = None

    def connect(self):
        pool = redis.ConnectionPool(**self.kargs)
        self.r = redis.Redis(connection_pool=pool)
        if self.r.ping():
            return self.r
        

remote_rc = Redis(CONFIG["ftp_redis"]).connect()

local_rc = Redis(CONFIG["local_redis"]).connect()




