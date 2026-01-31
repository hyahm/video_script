# encoding=utf-8

from service.redis import DELETE, remote_rc, DOWNLOADING, DELETE
from common.log import log


def add_downloading(filename):
    try:
        log.info("insert to downloading")
        remote_rc.sadd(DOWNLOADING, filename)
    except:
        # 如果没插入成功, 如果不是一直重复上传一个视频也没事
        log.error("insert downloading to redis failed")
        pass

def del_downloading(filename):
    log.info("delete downloading", 1)
    try:
        remote_rc.srem(DOWNLOADING, filename)
    except:
        # 如果没插入成功就无视
        pass
    
def need_delete(filename) -> bool:
    log.info("delete check", 1)
    try:
        ok = remote_rc.sismember(DELETE, filename)
        if ok:
            
            remote_rc.srem(DELETE, filename)
            remote_rc.srem(DOWNLOADING, filename)
        return ok
    except:
        # 如果没插入成功就无视
        return True
    

def is_downloading(filename):
    try:
        return remote_rc.sismember(DOWNLOADING, filename)
    except Exception as e:
        print(e)
        # 如果没插入成功就无视
        return False