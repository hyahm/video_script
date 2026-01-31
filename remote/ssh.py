# encoding=utf-8

import paramiko
import os
import sys

home = os.path.expanduser("~")
print(home)


class SSH():

    def __init__(self, host: str, port: int = 22, user: str = "root") -> None:
        private_key = paramiko.RSAKey.from_private_key_file(os.path.join(home ,'.ssh/id_rsa'))
        
        # 创建SSH对象
        self.ssh = paramiko.SSHClient()
        # 允许连接不在know_hosts文件中的主机
        self.ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        # 连接服务器
        self.ssh.connect(hostname=host, port=port, username=user, pkey=private_key)

        transport = paramiko.Transport((host, port))
        transport.connect(username=user, pkey=private_key )
        self.sftp = paramiko.SFTPClient.from_transport(transport)
        

    def mkdir(self, path):
        self.ssh.exec_command("mkdir -p " + path)

    def exec(self, command):
        stdin, stdout, stderr = self.ssh.exec_command(command=command)
        result = stdout.read()
        print(result.decode("utf-8"))

    def upload_file(self, local, remote):
        self.sftp.put(local, remote)

    def uploadDir(self, local_dir, remote_dir):
        # if local_dir[-1] != "\\" or local_dir[-1] != "/":
        local_abs = local_dir
        if sys.platform == "win32":
            if local_dir[-1] != "\\":
                local_abs = local_dir + "\\"
        else:
            if local_dir[-1] != "/":
                local_abs = local_dir + "/"
        self.ssh.exec_command("mkdir -p " + remote_dir)
        
        # sftp.mkdir(remote_root)
        files = os.walk(local_dir)
        for parent, _, filenames in files:
            # parent 目录的绝对路径
            # filename： 是目录下面的文件名
            reative = parent.replace(local_abs, "")
            self.ssh.exec_command("mkdir -p " + os.path.join(remote_dir,reative).replace("\\", "/"))
            # self.mkdir(reative)
            for filename in filenames:
                remote_file = os.path.join(remote_dir, reative, filename)
                local_file = os.path.join(parent, filename)
                self.sftp.put(local_file, remote_file.replace("\\", "/"), confirm=True)
            # self.upload_file( os.path.join(parent, filename), os.path.join(remote_dir, reative, filename))
            # print(reative)
            # print(filename)
            
        # 执行命令
        # stdin, stdout, stderr = ssh.exec_command('df')
        # 获取命令结果
        # result = stdout.read()
        # print(result)
    def upload_file(self, local_file, remote_file):
        self.sftp.put(local_file, remote_file)

    def close(self):
        self.sftp.close()
        self.ssh.close()
# 关闭连接
# ssh.close()


ssh = SSH("192.168.50.250")

ssh.uploadDir("D:\\scs", "/home/scs")
# ssh.upload_file("/mnt/d/scs/test.py", "/home/scs/test.py")

# ssh.upload_file("D:\\scs\\test.py", "/home/scs/pool.py")
# ssh.exec("ls")

# files = os.listdir("/mnt/d/scs")
# for x in files:
#     if os.path.isdir(x):
#         print("dir: " + x)
#     else:
#         print("file: " + x)