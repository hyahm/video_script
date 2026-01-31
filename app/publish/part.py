# encoding=utf-8

import imp
from lib.ffmpeg import FFmpegVideo
from os import path
import os
from common.ffmpeg import ffmpeg
import time
from common.shell import shell
from internal.var import iswindows

class CutPartVideo():
    def __init__(self, identifier: str, source_dir: str, video_path: str, video_length: int) -> None:
        self.source_dir = source_dir
        self.video_path = video_path
        self.video_length = video_length
        self.identifier = identifier
        self.cut_part_path = path.join(
            self.source_dir, "part_" + self.identifier + ".mp4")
        self.cut_large_part_path = path.join(
            self.source_dir, "large_part_" + self.identifier + ".mp4")
        self.tmpdir = str(time.time())

    def make_part_video(self):
        # 给最后的时间留1秒
        part = (self.video_length -1) // 9
        sv = FFmpegVideo()
        sv.input_file = self.video_path

        sv.step = 1
        try:
            os.mkdir(self.tmpdir)
        except:
            pass
        input_list = []
        large_input_list = []
        for i in range(10):
            sv.start = i*part
            sv.output_file = path.join(self.tmpdir, "%d.mp4" % i)
            large_output_file = path.join(self.tmpdir, "large_%d.mp4" % i)
            # 忽略失败
            if not ffmpeg.scale_video(sv):
                continue
            vc, ac, _ = ffmpeg.get_vcode(sv.output_file)
            if not vc or not ac:
                continue
            input_list.append(sv.output_file)

            if not ffmpeg.cut(self.video_path,large_output_file,sv.start, sv.step):
                continue
            large_input_list.append(large_output_file)
        if len(input_list) < 8:
            return False
        # 合并视频
        if not ffmpeg.merge_mp4_video(self.cut_part_path,*input_list):
            return False

        if not ffmpeg.merge_mp4_video(self.cut_large_part_path,*large_input_list):
            return False
        return True