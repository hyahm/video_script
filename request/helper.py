import time

def retry(times=3, second=1):  # 重试时间为一秒，重试次数为3次
    def decorator(func):
        def wrapper(*args, **kwargs):
            i = 0
            result = func(*args, **kwargs)
            while not result and i < times:
                time.sleep(second)
                i += 1
                result = func(*args, **kwargs)
            return result
        return wrapper
    return decorator
