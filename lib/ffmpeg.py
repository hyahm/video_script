'''
Author: your name
Date: 2022-02-12 21:01:20
LastEditTime: 2022-02-13 18:37:36
LastEditors: Please set LastEditors
Description: 打开koroFileHeader查看配置 进行设置: https://github.com/OBKoro1/koro1FileHeader/wiki/%E9%85%8D%E7%BD%AE
FilePath: /hugo_scripts/lib/ffmpeg.py
'''
from lib.base import filed_to_int, filed_to_dict, filed_to_list, filed_to_str
# from copy import deepcopy
import json
from typing import Dict

class FFFormat():
    def __init__(self, kargs: Dict) -> None:
        self.filename = filed_to_str(kargs, "filename", "")
        self.nb_streams = filed_to_int(kargs, "nb_streams", 0)
        self.nb_programs = filed_to_int(kargs, "nb_programs", 0)
        self.probe_score = filed_to_int(kargs, "probe_score", 0)
        self.format_name = filed_to_str(kargs, "format_name", "")
        self.format_long_name = filed_to_str(kargs, "format_long_name", "")
        self.start_time = filed_to_str(kargs, "start_time", "")
        self.duration = filed_to_str(kargs, "duration", "")
        self.size = filed_to_str(kargs, "size", "")
        self.bit_rate = filed_to_str(kargs, "bit_rate", "")
       

class Stream():
    def __init__(self, stream: Dict) -> None:
        self.index = filed_to_int(stream, "index", 0)
        self.codec_name = filed_to_str(stream, "codec_name", "")
        self.codec_long_name = filed_to_str(stream, "codec_long_name", "")
        self.profile = filed_to_str(stream, "profile", "")
        self.codec_type = filed_to_str(stream, "codec_type", "")
        self.codec_time_base = filed_to_str(stream, "codec_time_base", "")
        self.codec_tag_string = filed_to_str(stream, "codec_tag_string", "")
        self.codec_tag = filed_to_str(stream, "codec_tag", "")
        self.width = filed_to_int(stream, "width", 0)
        self.height = filed_to_int(stream, "height", 0)
        self.coded_width = filed_to_int(stream, "coded_width", 0)
        self.coded_height = filed_to_int(stream, "coded_height", 0)
        self.has_b_frames = filed_to_int(stream, "has_b_frames", 0)
        self.sample_aspect_ratio = filed_to_str(stream, "sample_aspect_ratio", "")
        self.display_aspect_ratio = filed_to_str(stream, "display_aspect_ratio", "")
        self.pix_fmt = filed_to_str(stream, "pix_fmt", "")
        self.level = filed_to_int(stream, "level", 0)
        self.chroma_location = filed_to_str(stream, "chroma_location", "")
        self.refs = filed_to_int(stream, "refs", 0)
        self.is_avc = filed_to_str(stream, "is_avc", "")
        self.nal_length_size = filed_to_str(stream, "nal_length_size", "")
        self.r_frame_rate = filed_to_str(stream, "r_frame_rate", "")
        self.avg_frame_rate = filed_to_str(stream, "avg_frame_rate", "")
        self.time_base = filed_to_str(stream, "time_base", "")
        self.start_pts = filed_to_int(stream, "start_pts", 0)
        self.start_time = filed_to_str(stream, "start_time", "")
        self.duration_ts = filed_to_int(stream, "duration_ts", 0)
        self.bits_per_sample = filed_to_int(stream, "bits_per_sample", 0)
        self.duration = filed_to_str(stream, "duration", "")
        self.bit_rate = filed_to_str(stream, "bit_rate", "")
        self.bits_per_raw_sample = filed_to_str(stream, "bits_per_raw_sample", "")
        self.nb_frames = filed_to_str(stream, "nb_frames", "")
        self.sample_fmt = filed_to_str(stream, "sample_fmt", "")
        self.sample_rate = filed_to_str(stream, "sample_rate", "")
        self.channels = filed_to_int(stream, "channels", "")
        self.channel_layout = filed_to_str(stream, "channel_layout", "")
        self.max_bit_rate = filed_to_str(stream, "max_bit_rate", "")

# probe 打印的消息
class FFprobeJson():
    def __init__(self, info: Dict) -> None:
        self.streams= []
        for stream in filed_to_list(info,"streams", [{},{}]):
            self.streams.append(Stream(stream))
        self.format = FFFormat(filed_to_dict(info,"format", {}))

    def dict(self):
        data = {}
        data["streams"] = []
        for stream in self.streams:
            data["streams"].append(stream.__dict__)
        data["format"] = self.format.__dict__
        return data

    def __str__(self):
        return json.dumps(self.dict())

class FFmpegVideo:
    def __init__(self) -> None:
        self.start:int = 0
        self.step:int = 1
        self.input_file:str = ""
        self.output_file:str = ""
        # "266:150 视频的大小  352 * 198
        self.scale:str = ""
        # 266:150:0:108:black 前面2位， 视频画布大小， 后2位是视频的起始位置x:y， 最后一个black是填充的颜色
        self.pad:str = ""


