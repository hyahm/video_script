# encoding=utf-8
import random
from common.log import log


def encrpyt_from_file(src, dst)->bool:
    """
    随机生成一个数， 将这个数跟后面数做 异或运算 追加到列表， 生成加密图片
    """
    mask = random.randint(0,255)
    tmp = []
    try:
        with open(src, 'rb') as f:
            a = f.read()
            tmp.append(mask)
            for i in a:
                tmp.append(i ^ mask)
        
        with open(dst, "wb+") as w:
            w.write(bytes(tmp))
        return True
    except Exception as e:
        log.error(e)
        return False


# def decrypt_from_file(src, dst):
#     w = []
#     f = open(src, 'rb')
#     a = f.read()
#     mask = int(a[0])
#     for i in a[1:]:
#         w.append(int(i) ^ mask)

#     with open(dst, "wb+") as w:
#         w.write(bytes(tmp))