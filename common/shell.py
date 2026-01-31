# -*- coding: UTF-8 -*-

import subprocess
import shutil
from common.log import log
import os
from typing import Tuple

# 执行shell命令


class Shell():
    def __init__(self):
        self.result = None
        self.err = ""
        self.code = 0
        self.out = ""

    def run(self, cmd) -> Tuple[bytes, int]:
        """
            return: 信息， 返回码
        """
        try:
            self.result = subprocess.run(
                cmd, shell=True, bufsize=16384, capture_output=True)
        except Exception as e:
            log.info(e)
            return "", 200
        self.err = self.result.stderr
        self.code = self.result.returncode
        self.out = self.result.stdout
        if self.code != 0:
            try:
                log.info(self.err.decode("utf-8"))
            except:
                pass
        return self.out, self.code

    # def rsync(self, src, dst) -> bool:
    #     """
    #     同步文件到目录
    #     :param src: 源文件
    #     :param dst: 目标文件
    #     :return: bool
    #     """
    #     cmd = "rsync -a --remove-source-files {0} {1}".format(src, dst)
    #     log.info(cmd, 1)
    #     _, code = self.run(cmd)
    #     return code == 0

    def copy(self, src, dst) -> None:
        """
        复制文件到文件夹下面
        :param src:
        :param dst:
        :return:
        """
        shutil.copyfile(src, dst)
        # cmd = "cp -f {} {}".format(src, dst)
        # log.info(cmd, 1)
        # _, code = self.run(cmd)
        # return code == 0

    def remove_all(self, rmfile) -> None:
        """
        删除所有文件夹或文件
        :param rmfile:  删除的文件或文件夹
        :return: bool
        """
        log.info("remove: " + rmfile, 1)
        if os.path.isfile(rmfile):
            os.remove(rmfile)
            return
        shutil.rmtree(rmfile, ignore_errors=True)

    def move_to(self, src, dst) -> None:
        """
        移动文件或目录
        :param src: 源文件
        :param dst: 目标
        :return: bool
        """
        log.info(src + " ----> " + dst)
        try:
            shutil.move(src, dst)
        except:
            pass

    def makedir(self, dir_name) -> None:
        '''
        创建dirName目录
        :param dir_name: 目录名称
        :return: bool
        '''
        os.makedirs(dir_name, exist_ok=True)

    # def make_host_port(self, server) -> Tuple[str, int]:
    #     """
    #     return: 返回服务器地址和端口
    #     """
    #     if server.count(":") > 0:
    #         s = server.split(":")
    #         try:
    #             port = int(s[1])
    #             return s[0], port
    #         except:
    #             pass
    #     return server, 22

    # def make_remote_dirs(self, remoteDir, server) -> bool:
    #     if server == "":
    #         server = self.resource.ip
    #     host, port = self.make_host_port(server)
    #     cmd = "ssh -p {} {}@{} mkdir -p {}".format(port, self.user, host, remoteDir)
    #     log.info(cmd, 1)
    #     _, code = self.run(cmd)
    #     return code == 0

    # # server 远程服务器的ip和端口
    # def rsync_to_server(self, local, remote, server) -> bool:
    #     # rsync -artuz -R  <第一级目录> caesar@23.224.1.106::resources --password-file=/etc/rsync.passwd
    #     # self.make_remote_dirs(remote, server)
    #     host, port = self.make_host_port(server)
    #     cmd = "rsync -artuz '-e ssh -p {}' {} {}@{}:{} --progress".format(
    #         port, local, self.user, host, remote)
    #     log.info(cmd, 1)
    #     _, code = self.run(cmd)
    #     return code == 0 or code == 24

    # # 资源文件只保留一份
    # def rsync_to_resource(self, local, remoteDir, filename, server) -> bool:
    #     host, port = self.make_host_port(server)
    #     # rsync -artuz -R  <第一级目录> caesar@23.224.1.106::resources --password-file=/etc/rsync.passwd
    #     # self.make_remote_dirs(remote, server)
    #     remote = join(remoteDir, filename)
    #     if filename == "":
    #         remote += "/"
    #     cmd = "rsync -artuz '-e ssh -p {}' {} {}@{}:{} --progress".format(
    #         port, local, self.user, host, remote)
    #     log.info(cmd, 1)
    #     _, code = self.run(cmd)
    #     return code == 0 or code == 24

    # # 资源文件只保留一份
    # def download_from_resource(self, remoteFile, localFile, server) -> bool:
    #     host, port = self.make_host_port(server)
    #     # rsync -artu  caesar@23.224.1.106::resources/dianying/test/food1.mp4 . --password-file=/etc/rsync.passwd
    #     cmd = "scp -P {} {}@{}:{} {} ".format(port, self.user, host ,remoteFile, localFile)
    #     log.info(cmd, 1)
    #     _, code = self.run(cmd)
    #     return code == 0 or code == 24


shell = Shell()
