# encoding=utf-8

## 腾讯sdk : https://cloud.tencent.com/document/product/436/12269
from common.log import log
import string
from qcloud_cos import CosConfig
from qcloud_cos import CosS3Client
from os import path
import logging
from pydantic import BaseModel
from lib.serverinfo import Server
from dataclasses import dataclass
import sys

logging.basicConfig(level=logging.INFO, stream=sys.stdout)
def to_camel(string: str) -> str:
    return ''.join(word.capitalize() for word in string.split('_'))

class TxOssResponse(BaseModel):
    content_length: int
    content_length: int


    class Config:
        alias_generator = to_camel

@dataclass(match_args=False)
class TxOss():
    def __init__(self, server: Server, scheme="https"):
        self.access_key_id = server.access_key_id
        self.access_key_secret =server.access_key_secret
        self.region: str = server.region
        self.bucket: str = server.bucket
        self.token: str = ''
        self.scheme: str= scheme
        config = CosConfig(Region=self.region, SecretId=self.access_key_id, SecretKey=self.access_key_secret, Token=self.token, Scheme=self.scheme)
        self.client = CosS3Client(config)

    # 上传文件
    def upload(self, filename: string, dir: str = "", dst: str = "")-> str:
        if dst == "":
            dst = path.basename(filename)
        dst = path.join(dir, dst).replace("\\", "/")
        log.info(dst)
        try:
            with open(filename, 'rb') as fp:
                response = self.client.put_object(
                    Bucket=self.bucket,
                    Body=fp,
                    Key=dst,
                    StorageClass='STANDARD',
                    EnableMD5=False
                )
                print(response)
            
            return "{}://{}.cos.{}.myqcloud.com/{}".format(self.scheme,self.bucket,self.region, dst)
        except Exception as e:
            print(e)
            return False
    # 获取文件的名字

    # 上传hls
    def upload_hls(self, filename: string, dst: str = "")-> str:
        if dst == "":
            dst = path.basename(filename)
        with open(filename, 'rb') as fp:
            response = self.client.put_object(
                Bucket=self.bucket,
                Body=fp,
                Key=dst,
                StorageClass='STANDARD',
                EnableMD5=False
            )
        return "{}://{}.cos.{}.myqcloud.com/{}".format(self.scheme,self.bucket,self.region,dst)