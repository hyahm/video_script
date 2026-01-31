from elasticsearch import Elasticsearch
import time
from common.log import log

INDEX = "hugo"

class Es():
    def __init__(self):
        try:
            self.es = Elasticsearch([
                    {'host': "3.1.219.46"},
                ], http_auth=('elastic', '9EfhUxW$b!CClSX9iUFJofo4'), port=9200)
        except Exception as e:
            raise Exception(e)


    def create_index(self, index):
        try:
            self.es.indices.create(index=index, ignore=400)
            return True
        except Exception as e:
            log.error(e)
            return False
    
 

    def create(self, data, index=INDEX):
        try:
            self.create_index(index)
            now = int(time.time())
            self.es.create(index=index,id=now, body=data)
            log.info("success")
            return True
        except Exception as e:
            log.error(e)
            return False

    def delelte(self, index):
        try:
            
            delete_by_all = {"query":{"match_all":{}}}
            x = self.es.delete_by_query(index=index, body=delete_by_all)
            log.info(x)
            return True
        except Exception as e:
            log.error(e)
            return False
es = Es()
es.create_index(INDEX)