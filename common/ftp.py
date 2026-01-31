# encoding=utf-8



from service.ftp import ConnectFtp

class FtpClient():
    def __init__(self,filename, ftp: ConnectFtp, directory=""):
        self.ftp = ftp
        self.directory = directory
        self.filename = filename
        self.ftp.cd("/" + self.directory)
        self.err = ""
        
    def renameappend(self, append: str) -> bool:
        # append： 追加的错误
        ok = self.ftp.rename(self.filename, self.filename + append)
        if not ok:
            self.err = "rename file error"
        return bool(ok)
    
    def download(self, dstfile) -> bool:
        ok = self.ftp.download(self.filename, dstfile)
        if not ok:
            self.err = "download file error"
        return ok
    
    def get_size(self, ftpfile) -> int:
        size = self.ftp.getsize(ftpfile)
        if not size:
            self.err = " file size is zero"
        return size
    
    def is_uploading(self, ftpfile) -> bool:
        return self.ftp.is_uploading(ftpfile)
    
    def exsit(self, file) -> bool:
        return file in self.ls()

    def ls(self, directory="") -> list:
        return self.ftp.ls(directory)