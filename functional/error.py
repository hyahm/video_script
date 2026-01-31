# encoding=utf-8

import json
from common.log import log


def except_handle(name):
    
    def wrapper(*arg):
        try:
            name(*arg)
        except Exception as e:
            error = ""
            for arg in e.args:
                if isinstance(arg, str):
                    error += arg + "\n"
                elif isinstance(arg, bytes):
                    error += arg.decode("utf-8") + "\n"
                elif isinstance(arg, int or bool):
                    error += str(arg) + "\n"
                else:
                    error += json.dumps(arg) + "\n"
            error = error[:-1]
            log.error(error)
    return wrapper