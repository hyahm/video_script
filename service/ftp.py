# -*- coding: UTF-8 -*-

from ftplib import FTP
from common.log import log
import time


class ConnectFtp(object):
    """
    连接FTP
    :return: ftp对象
    """

    def error(self):
        return self._error

    def parse_e(self, e: Exception):
        if len(e.args) > 0:
            self._error = str(e.args[0])
        else:
            self._error = str(e)

    def __init__(self, host: str,  user: str, pwd: str, port: int = 21, dir:str = "", timeout: int= None):
        self.connect_failed = "[Error]: FTP connect failed."
        self.host = host
        self.port = port
        self.user = user
        self._error = None
        self.timeout= timeout
        self.password = pwd
        self.dir = dir
        if self.port == 0:
            self.port = 21
        # self.timeout = timeout
        log.info("{},{},{},{}".format(self.host,self.port ,self.user , self.password))
        self.ftp = FTP()
        log.info("connect ftp")
        wecome =  self.ftp.connect(self.host, self.port, self.timeout)
        log.info(wecome)
        msg = self.ftp.login(self.user, self.password)
        self.cd(self.dir)
        log.info(msg)

    def connect(self):
        try:
            log.info("connect ftp")
            wecome = self.ftp.connect(self.host, self.port,self.timeout)
            log.info(wecome)
            msg = self.ftp.login(self.user, self.password)
            self.cd(self.dir)
            log.info(msg)
            return True
        except Exception as e:
            self.parse_e(e)
            return False

    def ls(self, path="."):
        if self._check():
            try:
                return self.ftp.nlst(path)
            except Exception as e:
                self.parse_e(e)
                return []
        self._error = self.connect_failed
        return []

    def getsize(self, file):
        try:
            return self.ftp.size(file)
        except Exception as e:
            self.parse_e(e)
            return 0

    def exist(self, file):
        return file in self.ls(".")

    def ll(self, path):
        if self._check():
            try:
                return self.ftp.dir(path)
            except Exception as e:
                self.parse_e(e)
                return ""
        self._error = self.connect_failed
        return ""

    def close(self):
        try:
            log.info("close ftp")
            self.ftp.close()
        except:
            pass

    def _check(self):
        if not self.ping() and not self.connect():
            self._error = self.connect_failed
            return False
        return True

    def cmd(self, cmd):
        if self._check():
            try:
                return self.ftp.sendcmd(cmd)
            except Exception as e:
                self.parse_e(e)
                return None
        self._error = self.connect_failed
        return None

    def ping(self):
        try:
            return self.ftp.pwd()
        except Exception as e:
            self.parse_e(e)
            return ""

    def set_pasv(self, val=True):
        pass

    def dir(self, path=""):
        try:
            return self.ftp.dir(path)
        except Exception as e:
            self.parse_e(e)
            return ""

    def mkdir(self, path):
        try:
            self.ftp.mkd(path)
            return True
        except Exception as e:
            self.parse_e(e)
            return False

    def cd(self, path):
        try:
            return self.ftp.cwd(path)
        except Exception as e:
            self.parse_e(e)
            return ""

    def rmdir(self, path):
        try:
            return self.ftp.rmd(path)
        except Exception as e:
            self.parse_e(e)
            return False

    def pwd(self):
        try:
            return self.ftp.pwd()
        except Exception as e:
            self.parse_e(e)
            return ""

    def delete(self, filename):
        log.info("delete ftp: " + filename)
        try:
            return self.ftp.delete(filename)
        except:
            return False

    def download(self, remote_file, local_file, timeout=None):
        try:
            import socket
            socket.setdefaulttimeout(timeout)
            buff_size = 1024
            with open(local_file, "wb") as fp:
                self.ftp.retrbinary(
                    "RETR " + remote_file, fp.write, buff_size)
            log.info("download %s seccess" % remote_file)
            return True
        except Exception as e:
            self.parse_e(e)
            return False

    def upload(self, remote_file, local_file):
        try:
            with open(local_file, "rb") as fp:
                self.ftp.storbinary("STOR " + remote_file, fp)
            return True
        except Exception as e:
            self.parse_e(e)
            return False

    def is_uploading(self, file):
        first = self.mdtm(file)
        time.sleep(1)
        second = self.mdtm(file)
        # 检查文件是否在下载
        return first != second

    def retrlines(self, file_list):
        if self._check():
            try:
                return self.ftp.retrlines("LIST", file_list.append)
            except Exception as e:
                self.parse_e(e)
                return False
        self._error = self.connect_failed
        return ""

    def mdtm(self, vd_remote_path):
        if self._check():
            try:
                tt = self.ftp.sendcmd("MDTM " + vd_remote_path)
                return int(tt.split(" ")[1])
            except Exception as e:
                self.parse_e(e)
                return 0
        self._error = self.connect_failed
        return 0

    def rename(self, name, newname):
        if self._check():
            try:
                return self.ftp.rename(name, newname)
            except Exception as e:
                self.parse_e(e)
                return False
        self._error = self.connect_failed
        return False


# loopftp使用的
# ftp = Connect(CONFIG["ftp_host"], CONFIG["ftp_port"],
#               CONFIG["ftp_user"], CONFIG["ftp_pwd"])



