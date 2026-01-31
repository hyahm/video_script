import requests
import json
from config import CONFIG
import os
from common.log import log
requests.packages.urllib3.disable_warnings()

class Scs():
    # 报警用副本名来作为第一唯一标识
    
    def __init__(self, url="https://127.0.0.1:11111", pname=os.getenv("NAME"), name=os.getenv("NAME"), token=os.getenv("TOKEN")):
        self._url = url
        self._headers = {
            "Token": token
        }
        
        self._data = {
            "pname": pname, 
            "name": name, 
        }
        
    def set_pname(self, pname):
        self._data["pname"] = pname
    
    def set_name(self, name):
        self._data["name"] = name
    
    def get_pname(self):
        return self._data["pname"]
    
    def get_name(self):
        return self._data["name"]
    
    def can_stop(self):
        self._data["value"] = False
        try:
            requests.post("{}/change/signal".format(self._url), data=json.dumps(self._data),headers = self._headers, verify=False)
        except Exception as e:
            log.error(e)


    def can_not_stop(self):
        self._data["value"] = True
        try:
            requests.post("{}/change/signal".format(self._url), headers = self._headers, data=json.dumps(self._data), verify=False)
        except Exception as e:
            log.error(e)
        
    def set_version(self, version):
        try:
            requests.get("{}/version/{}/{}?version={}".format(self._url, self._data["pname"], self._data["name"], version),headers = self._headers, timeout=1, verify=False)
        except Exception as e:
            log.error(e)

scs = Scs(CONFIG["scs"]["domain"])