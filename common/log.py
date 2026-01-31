# encoding=utf-8
import os
import time
import sys
from enum import IntEnum
from pyscs.alert import Alert
from pyscs.scs import SCS
from config import CONFIG
import json

class Level(IntEnum):
    TRACE = 0
    DEBUG = 1
    INFO = 2
    WARNING = 3
    ERROR = 4

class Log():
    def __init__(self):
        self._dir = "log"
        self.set_dir(self._dir)
        # 每日切割， 优先大小切割
        self._every = True
        self._out = CONFIG.get("debug", False)
        self._log_name = "info.log"
        # 大小切割
        self._size = 0
        self._level = 2
        self._day = time.strftime("%Y-%m-%d")
        self._f = None
        self.scs = SCS()
        self.alert = Alert()
        self.alert.pname = os.getenv("PNAME")
        self.alert.name = os.getenv("NAME")
        self.alert.title = "code error"
        self._disable_alert = False
        
    
    def set_out(self, out: bool) -> None:
        # 设置是否在控制台输出， 否则就文件
        self._out = bool(out)
        
    def set_disable_alert(self, out: bool) -> None:
        # 设置是否在控制台输出， 否则就文件
        self._disable_alert = bool(out)
        
    def set_level(self, level: Level) -> None:
        # 设置是否在控制台输出， 否则就文件
        self._level = level

    def set_dir(self, dir: str) -> None:
        # 设置日志目录
        self._dir = os.path.normpath(dir)
        os.makedirs(self._dir, exist_ok=True)
        if os.path.isfile(self._dir):
            raise Exception("{} have file".format(self._dir))      
    
    def _make_dir(self) -> None:
        os.makedirs(self._dir, exist_ok=True)

    def set_every(self, every: bool) -> None:
        # 设置是否每天备份
        self._every = bool(every)

    def set_size(self, size: int):
        # 设置切割日志的大小， 如果设置了每天备份， 此处不生效
        if not isinstance(size, int):
            raise Exception("size must be int type") 
        self._size = size

    def set_log_name(self, name: str) -> None:
        # 设置info类型的文件名
        self._log_name = name
    
    def trace(self, msg="", deep=0) -> None:
        if self._level > 1:
            return
        self._append_log( msg, "INFO", deep)

    def info(self, msg="", deep=0) -> None:
        if self._level > 3:
            return
        self._append_log( msg, "INFO", deep)
    
    def set_name(self, name: str) -> None:
        self.alert.name = name
        
    def set_title(self, title) -> None:
        self.alert.title = title

    def error(self, msg=None,deep=0) -> None:
        if isinstance(msg, dict):
            msg = json.dumps(msg)
        if not self._disable_alert:
            self.alert.pname = self.scs.get_name()
            self.alert.reason = str(msg)
            try:
                self.scs.send_alert(self.alert)
            except:
                pass
        # 必须会显示， 无法隐藏
        self._append_log(msg, "ERROR", deep)

    def debug(self, msg="",deep=0) -> None:
        if self._level > 2:
            return
        self._append_log(msg, "DEBUG", deep)

    def warning(self, msg="",deep=0) -> None:
        if self._level > 4:
            return
        self._append_log(msg, "WARNING", deep)

    def _currentframe(self):
        try:
            raise Exception
        except:
            return sys.exc_info()[2].tb_frame.f_back
    
    def _findCaller(self, deep):
        
        self._f = self._currentframe()
        if self._f is not None:
                self._f = self._f.f_back.f_back.f_back
        for _ in range(deep):
            self._f = self._f.f_back
        if hasattr(self._f, "f_code"):
            co = self._f.f_code
            return co.co_filename, self._f.f_lineno    
        else:
            return "deep error", 0   
     
    def _append_log(self, data, level="", deep=2) -> None:
        now = time.strftime("%Y-%m-%d %H:%M:%S")
        name, no = self._findCaller(deep)
        if no == 0:
            level = "ERROR"
        prefix = "{} - {}:{}".format(now, name, no)
        
        if self._out:
            print("{} - [{}] - {}".format(prefix,level, data), flush=True)
            return
        else:
            this_log_file = os.path.join(self._dir, self._log_name)
            this_day = time.strftime("%Y-%m-%d")
            if self._every and self._day != this_day:
                if os.path.exists(this_log_file):
                    os.rename(this_log_file, os.path.join(self._dir, self._day + "_" + self._log_name))
                self._day = this_day
            # elif self._size > 0:
            #     if os.path.exists(this_log_file):
            #         size = os.path.getsize(this_log_file)
            #         if size > self._size * 1024 * 1024:
            #             pre_name = str(time.time())
            #             os.rename(this_log_file, os.path.join(self._dir, pre_name + "_" + self._log_name))
            
            try:
                with open(this_log_file, "a+") as f:
                    f.write("{} - [{}] - {} \n".format(prefix,level, data))
            except FileNotFoundError:
                # 一次失败重试的机会， 如果重试失败， 设置为stdout输出
                ok = os.path.exists(self._dir)
                if not ok:
                    os.makedirs(self._dir, exist_ok=True)
                with open(this_log_file, "a+") as f:
                    f.write("{} - [{}] - {} \n".format(prefix,level, data))
log = Log()


