# encoding=utf-8

import unittest

from lib.base import filed_to_bool, filed_to_dict, filed_to_int, filed_to_list, filed_to_str
from common.log import log
log.set_out(True)

class TestStringMethods(unittest.TestCase):

    def test_dict(self) -> None:
        testdata = [1, "asdf", False]
        for value in testdata:
            self.assertEqual(filed_to_bool(value, "key"), False)
            self.assertEqual(filed_to_dict(value, "key"), {})
            self.assertEqual(filed_to_int(value, "key"), 0)
            self.assertEqual(filed_to_list(value, "key"), [])
            self.assertEqual(filed_to_str(value, "key"), "")

    def test_filed_to_bool(self) -> None:
        testdata = [
            {"key":"", "expect": False}, 
            {"key":"true", "expect": True},
             {"key":"false", "expect": False}, 
             {"key":"1", "expect": True}, 
             {"key":"0", "expect": False}, 
             {"key":1, "expect": True}, 
             {"key":0, "expect": False}
             ]
        for d in testdata:
            self.assertEqual(filed_to_bool(d, "key"), filed_to_bool(d, "expect"))
    
    def test_filed_to_dict(self) -> None:
        testdata = [
            {"key":"", "expect": {}}, 
            {"key":"{'aaa': 'bbb', 'ccc': false, 'ddd': false}", "expect": {}},
            {"key":'{"aaa": "bbb", "ccc": false, "ddd": false}', "expect": {"aaa": "bbb", "ccc": False, "ddd": False}},
            {"key":{"name":False, "aaa": False}, "expect": {"name":False, "aaa": False}}, 
        ]
        for d in testdata:
            self.assertEqual(filed_to_dict(d, "key"), filed_to_dict(d, "expect"))
                
    def test_filed_to_int(self) -> None:
        testdata = [
            {"key":"asd", "expect": 0}, 
            {"key":54, "expect": 54},
            {"key": "312", "expect": 0},
            {"key": 321.54, "expect": 321}, 
        ]
        for d in testdata:
            self.assertEqual(filed_to_int(d, "key"), filed_to_int(d, "expect"))

    def test_filed_to_list(self) -> None:
        testdata = [
            {"key":"asd", "expect": []}, 
            {"key": ["aaa", "bbb"], "expect": ["aaa", "bbb"]},
            {"key": [1, 2, 4, 6], "expect": [1, 2, 4, 6]},
            {"key": '["aaa", "bbb"]', "expect": ["aaa", "bbb"]}, 
            {"key": '{"aaa": "bbb"}', "expect": []}, 
        ]
        for d in testdata:
            self.assertEqual(filed_to_list(d, "key"), filed_to_list(d, "expect"))
    
    def test_filed_to_str(self) -> None:
        testdata = [
            {"key":"asd", "expect": "asd"}, 
            {"key": True, "expect": "true"},
            {"key": False, "expect": "false"},
            {"key": '["aaa", "bbb"]', "expect": '["aaa", "bbb"]'}, 
            {"key": '{"aaa": "bbb"}', "expect": '{"aaa": "bbb"}'}, 
            {"key": 54, "expect": "54"}, 
            {"key": 54.666, "expect": "54.666"}, 
        ]
        for d in testdata:
            self.assertEqual(filed_to_str(d, "key"), filed_to_str(d, "expect"))

if __name__ == '__main__':
    unittest.main()