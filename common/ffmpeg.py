# -*- coding: UTF-8 -*-

from common.shell import shell
from common.log import log
from os.path import join, normpath
from lib.newrule import Logo, Font
import json
from shutil import which
from lib.ffmpeg import FFmpegVideo,FFprobeJson
from typing import Tuple


class FFmpeg(object):
    def __init__(self):
        self._check()

    def _check(self):
        """
        检查FFmpeg是否正确配置
        :return: bool
        """
        if which("ffprobe") and which("ffmpeg"):
            return
        raise Exception("not found command ffprobe or ffmpeg ")

    def _run(self, cmd: str) -> bool:
        """
        运行COMMAND指令
        :param cmd: COMMAND指令
        :return:bool
        """
        log.info(cmd, 2)
        _, code = shell.run(cmd)
        return code == 0

    def get_json_info(self, input: str) -> FFprobeJson:
        input = normpath(input)
        cmd = 'ffprobe -v quiet -show_format -show_streams  -print_format json {}'.format(input)
        log.info(cmd)
        out, code = shell.run(cmd)
        if code == 0:
            try:
                data = json.loads(out.decode("utf-8"))
                return FFprobeJson(data)
            except Exception as e:
                log.info(e)
                return FFprobeJson({})
        return FFprobeJson({})

    def get_vcode(self, file_path) -> Tuple[bool, bool, int]:
        """
        # 获取视频，音频， 数据流个数
        获取视频的内部编码
        :param file_path: 视频文件的路径
        :return: 是否存在视频, 是否存在音频, 媒体流个数
        command: ffprobe -i xx.mp4 -v error -select_streams v:0 -show_entries stream=codec_name -of default=nw=1
        """
        file_path = normpath(file_path)
        data = self.get_json_info(file_path)
        audio = False
        video = False
        try:
            for stream in data.streams:
                if stream.codec_type == "video":
                    video = True
                if stream.codec_type == "audio":
                    audio = True
            return video, audio, data.format.nb_streams
        except:
            return video,audio, 0

    def get_video_length(self, file_path) -> int:
        """
        获取视频片长, 并不是format里面的
        :param file_path: 视频文件
        :return: int
        command: ffprobe -show_entries format=duration -v quiet -of csv="p=0" a.mp4
        """
        file_path = normpath(file_path)
        data = self.get_json_info(file_path)
        try:
            for stream in data.streams:
                if stream.codec_type == "video":
                    return int(float(stream.duration))
        except:
            return 0
        # duration = int(float(duration))
        # cmd = 'ffprobe -show_entries format=duration -v quiet -of csv="p=0" %s' % file_path
        # log.info(cmd, 1)
        # out, code = shell.run(cmd)
        # if code == 0:
        #     try:
        #         length = int(float(out.decode()))
        #         return length
        #     except:
        #         return 0

        # return 0

    def get_video_shape(self, file_path) -> Tuple[int, int]:
        """
        获取视频宽度和高度
        :param file:视频文件
        :return: 宽度 , 高度
        command: ffprobe -v error -select_streams v:0 -show_entries stream=width,height -of default=nw=1:nk=1 a.mp4
        """

        file_path = normpath(file_path)
        data = self.get_json_info(file_path)
        try:
            for v in data.streams:
                if v.codec_type == "video":
                    width = v.width
                    height = v.height
                    return width, height
        except:
            pass
        return 0, 0
    

    def change_shape(self, input_path, width, height, output_path) -> bool:
        """
        改变视频的比例
        :param input_path:输入视频路径
        :param width:宽度
        :param height:高度
        :param output_path:输出视频路径
        :return:bool
        """
        input_path = normpath(input_path)
        output_path = normpath(output_path)
        cmd = "ffmpeg -loglevel error -i {} -s {}*{} -y {}".format(
            input_path, width, height, output_path)
        return self._run(cmd)

    def to_mp4(self, input_path, output_path, start=0, to=0) -> bool:
        """
        转为 mp4 格式, 默认覆盖文件
        :param input_path: 源文件路径
        :param output_path: 输出文件路径
        :return: bool
        """
        input_path = normpath(input_path)
        output_path = normpath(output_path)
        if to == 0:
            cmd = "ffmpeg -loglevel error -ss {} -i {} -c:v h264 -c:a aac -map_metadata -1 -max_muxing_queue_size 9999 -y {}".format(
                start, input_path, output_path)
        else:
            cmd = "ffmpeg -loglevel error -ss {} -to {} -i {} -c:v h264 -c:a aac -map_metadata -1 -max_muxing_queue_size 9999 -y {}".format(
                start, to, input_path, output_path)
        return self._run(cmd)

    # def remove_stream_data(self, input_path, output_path) -> bool:
    #     """
    #     删除mp4 多余的stream
    #     :param input_path: 源文件路径
    #     :param output_path: 输出文件路径
    #     :return: bool
    #     """
    #     input_path = normpath(input_path)
    #     output_path = normpath(output_path)
    #     cmd = "ffmpeg -loglevel error -i {0} -c:a aac -c:v copy -max_muxing_queue_size 9999 -y {1}".format(
    #         input_path, output_path)
    #     return self._run(cmd)

    def resize(self, input_path, output_path, width, heigth) -> bool:
        """
        重新设置分辨率
        :param input_path: 源文件路径
        :param output_path: 输出文件路径
        :param width: 新的视频宽度
        :param heigth: 新的视频高度
        :return: bool
        command： ffmpeg -y -i u5.mp4  -vf scale=1146:480,setdar=1146:480 test480p.mp4 -hide_banner
        """

        input_path = normpath(input_path)
        output_path = normpath(output_path)
        cmd = "ffmpeg -y -loglevel error -i {} -vf scale={}:{},setdar={}/{} -max_muxing_queue_size 9999  {} -hide_banner".format(
            input_path, width, heigth, width, heigth, output_path)
        return self._run(cmd)

    def get_cover(self, input_path, second, output_path, size=None) -> bool:
        """
        获取多长时间的图片作为封面
        :param input_path: 源视频文件
        :param second: 哪一秒的图片
        :param size: 图片高度宽度 w*h
        :param output_path: 保存的图片路径
        :return: bool

        command: ffmpeg -i a.mp4 -y -f image2 -ss 1 -vframes 1  output.jpg
        """
        input_path = normpath(input_path)
        output_path = normpath(output_path)
        if size:
            cmd = "ffmpeg -y -loglevel error -ss {} -i {} -s {} -y -f image2  -vframes 1 {}".format(
                second, input_path, size, output_path)
        else:
            cmd = "ffmpeg -y -loglevel error -ss {} -i {} -y -f image2  -vframes 1 {}".format(
                second, input_path, output_path)
        return self._run(cmd)

    def screen_image(self, input_path, output_path, count=200, interval=1, size=None) -> bool:
        """
        从视频中截100张图
        :param input_path:  视频文件
        :param output_path:  输出目录
        :param count:  一共输出多少张图片（可能不会有这么多张， 与视频长度和间隔有关）
        :param interval: 每多少秒剪切一张
        :param size:   eg:10*10, 默认视频分辨率
        :return: bool
        command: ffmpeg -y -i mv_nPBSejLR.mp4 -vf fps=1/10 -q:v 2 -s 192*80 -f image2 -vframes 10 a%2d.jpg
        """
        input_path = normpath(input_path)
        output_path = normpath(output_path)
        cmd = ""
        if size:
            cmd = "ffmpeg -y -i %s -vf fps=1/%s -q:v 2 -s %s -f image2 -vframes %s %s" % \
                (input_path, interval, size, count, output_path)
        else:
            cmd = "ffmpeg -y -i %s -vf fps=1/%s -q:v 2 -f image2 -vframes %s %s" % \
                (input_path, interval, count, output_path)
        return self._run(cmd)

    def cut(self, input_path, output_path, start, step, size=None) -> bool:
        """
        前后时间切片
        :param input_path:原视频输入路径
        :param output_path: 结果输出路径
        :param start: 开始时间
        :param size: 视频尺寸 "310*174"
        :param step: 持续时间
        :return: bool
        """

        input_path = normpath(input_path)
        output_path = normpath(output_path)
        cmd = ""
        if size:
            cmd = "ffmpeg -loglevel error -ss {} -accurate_seek -t {} -i {} -s {} -y -max_muxing_queue_size 9999  -vcodec h264 {}".format(
                start, step, input_path, size, output_path)
        else:
            cmd = "ffmpeg -loglevel error -ss {} -accurate_seek -t {} -i {} -y -max_muxing_queue_size 9999  -vcodec h264 {}".format(
                start, step, input_path, output_path)
        return self._run(cmd)

    def cut_to_end(self, input_path, output_path, start, size="310*174") -> bool:
        """
        前后时间切片
        :param input_path:原视频输入路径
        :param output_path: 结果输出路径
        :param start: 开始时间
        :param size: 视频尺寸 "310*174"
        :return: bool
        """
        input_path = normpath(input_path)
        output_path = normpath(output_path)
        cmd = "ffmpeg -loglevel error -ss {} -accurate_seek -i {} -s {} -y {}".format(
            start, input_path, size, output_path)
        return self._run(cmd)

    def scroll(self, input_path, output_path, text, size, color, time, position) -> bool:
        """
        添加滚动文字
        :param input_path:原视频输入路径
        :param output_path:视频输出路径
        :param text:文字内容
        :param color:颜色
        :param time:滚动时间
        :param size:字体大小
        :param position:位置， 1，2，3   上中下
        :return: bool
        """
        input_path = normpath(input_path)
        output_path = normpath(output_path)
        if position == "1":
            position = "h*0.05"
        elif position == "2":
            position = "h/2"
        else:
            position = "h*0.9"
        font_file = __file__.replace("ffmpeg.py", "fonts/DejaVuSans.ttf")
        cmd = 'ffmpeg -loglevel error -i {} -c:a copy -filter:v drawtext="fontfile={}:text={}:fontsize={}:fontcolor={}:y={}:x=w-w/{}*mod(t\,{})" -y {}'.format(
            input_path, font_file, text, size, color, position, round(time*0.6, 1), time, output_path)
        return self._run(cmd)

    def watermark(self, input_path, output_path, image_path, position) -> bool:
        """
        添加水印图片
        :param input_path:输入视频路径
        :param output_path:输出视频路径
        :param image_path: 水印图片路径
        :param position: 水印图片位置
        :return: bool
        """
        input_path = normpath(input_path)
        output_path = normpath(output_path)
        image_path = normpath(image_path)
        if position == "1":
            overlay = "10:10"
        elif position == "2":
            overlay = "main_w-overlay_w-10:10"
        elif position == "3":
            overlay = "10:main_h-overlay_h-10"
        else:
            overlay = "main_w-overlay_w-10:main_h-overlay_h-10"
        cmd = "ffmpeg -loglevel error -i {} -c:a copy -vf \"movie={}[watermark];[in][watermark] overlay={}[out]\" -y {}".format(
            input_path, image_path, overlay, output_path)
        return self._run(cmd)

    def u5_watermark(self, input_path, output_path, image_path, voice="aac", scale="-1:480") -> bool:
        """
        添加水印图片
        :param input_path:输入视频路径
        :param output_path:输出视频路径
        :param image_path: 水印图片路径
        :param position: 水印图片位置
        :return: bool
        """
        # if position == "1":
        #     overlay = "10:10"
        # elif position == "2":
        #     overlay = "main_w-overlay_w-10:10"
        # elif position == "3":
        #     overlay = "10:main_h-overlay_h-10"
        # else:
        #     overlay = "main_w-overlay_w-10:main_h-overlay_h-10"
        # ffmpeg -loglevel error -i test.mp4 -i  tv_yUKMJjPb_03_water.png -filter_complex "[0:v]scale=-1:480[to];[to][1:v]overlay=x=main_w-overlay_w-20:y=20" -y a.mp4
        # if scale:
        #     cmd = "ffmpeg -loglevel error -i {} scale={} -c:a {} -vf \"movie={}[watermark];[in][watermark] overlay=main_w-overlay_w-20:20[out]\" -y {}".format(
        #                 input_path,scale, voice,image_path, output_path)
        # else:

        #     cmd = "ffmpeg -loglevel error -i {} -c:a {} -vf \"movie={}[watermark];[in][watermark] overlay=main_w-overlay_w-20:20[out]\" -y {}".format(
        #     input_path, voice, image_path, output_path)

        input_path = normpath(input_path)
        output_path = normpath(output_path)
        image_path = normpath(image_path)
        cmd = ""
        if scale:
            cmd = "ffmpeg -loglevel error -i {} -i  {} -c:a {} -filter_complex \"[0:v]scale={}[to];[to][1:v]overlay=x=main_w-overlay_w-20:y=20\" -y {}".format(
                input_path, image_path, voice, scale, output_path)
        else:
            cmd = "ffmpeg -loglevel error -i {} -i  {} -c:a {} -filter_complex \"overlay=x=main_w-overlay_w-20:y=20\" -y {}".format(
                input_path, image_path, voice, output_path)
        return self._run(cmd)

    def u5_to_480_right(self, input_path, output_path, image_path, voice="aac") -> bool:
        """
        添加水印图片
        :param input_path:输入视频路径
        :param output_path:输出视频路径
        :param image_path: 水印图片路径
        :param position: 水印图片位置
        :return: bool
        """
        input_path = normpath(input_path)
        output_path = normpath(output_path)
        image_path = normpath(image_path)
        #     cmd = "ffmpeg -loglevel error -i {} -c:a {} -vf \"movie={}[watermark];[in][watermark] overlay=main_w-overlay_w-20:20[out]\" -y {}".format(
        #     input_path, voice, image_path, output_path)

        cmd = "ffmpeg -loglevel error -i {} -i  {} -c:a {} -s hd480 -filter_complex \"[0:v][1:v]overlay=x=main_w-overlay_w-20:y=20\" -y {}".format(
            input_path, image_path, voice, output_path)
        return self._run(cmd)

    # def u5_to_480_left(self, input_path, output_path, image_path, voice="aac"):
    def u5_to_480_left(self, input_path, output_path, image_path, voice="aac") -> bool:
        """
        添加水印图片
        :param input_path:输入视频路径
        :param output_path:输出视频路径
        :param image_path: 水印图片路径
        :param position: 水印图片位置
        :return: bool
        """
        # 计算缩放后的宽度， 宽度必须是32的倍数
        # width, height = self.get_video_shape(input_path)

        #     cmd = "ffmpeg -loglevel error -i {} -c:a {} -vf \"movie={}[watermark];[in][watermark] overlay=main_w-overlay_w-20:20[out]\" -y {}".format(
        #     input_path, voice, image_path, output_path)

        # cmd = "ffmpeg -loglevel error -i {} -i  {} -c:a {} -max_muxing_queue_size 9999  -filter_complex \"[0:v]scale=-2:480[scale];[scale][1:v]overlay=x=20:y=20\" -y {}".format(
        #             input_path, image_path, voice, output_path)
        input_path = normpath(input_path)
        output_path = normpath(output_path)
        image_path = normpath(image_path)
        cmd = "ffmpeg -loglevel error -i {} -i  {} -c:a {} -max_muxing_queue_size 9999  -filter_complex \"[0:v][1:v]overlay=x=0:y=0\" -y {}".format(
            input_path, image_path, voice, output_path)
        return self._run(cmd)

    def to_ts(self, input_path, output_path) -> bool:
        """
        将输入视频转为ts分片视频格式
        :param input_path:输入视频路径
        :param output_path:输出视频路径
        :return:bool
        """
        input_path = normpath(input_path)
        output_path = normpath(output_path)
        cmd = "ffmpeg -loglevel error -i {} -vcodec copy -acodec copy -vbsf h264_mp4toannexb -y {}".format(
            input_path, output_path)
        return self._run(cmd)

    def merge_ts(self, ts_path, output_path, titles_path, credits_path) -> bool:
        """
        废弃
        将多个ts分片合并为mp4视频文件
        :param ts_path:ts格式的输入视频路径
        :param output_path:mp4格式的输出视频路径
        :param titles_path:ts格式的片头
        :param credits_path:ts格式的片尾
        :return:bool
        """
        cmd = ""
        if titles_path and credits_path:
            cmd = "ffmpeg -i \"concat:{}|{}|{}\" -acodec copy -vcodec copy -absf aac_adtstoasc -y {}".format(
                titles_path, ts_path, credits_path, output_path)
        elif titles_path:
            cmd = "ffmpeg -i \"concat:{}|{}\" -acodec copy -vcodec copy -absf aac_adtstoasc -y {}".format(
                titles_path, ts_path, output_path)
        elif credits_path:
            cmd = "ffmpeg -i \"concat:{}|{}\" -acodec copy -vcodec copy -absf aac_adtstoasc -y {}".format(
                ts_path, credits_path, output_path)
        return self._run(cmd)

    def merge_mp4_video(self, output_path, *input_file)->bool:
        """
        废弃
        :param output_path:mp4格式的输出视频路径
        :param titles_path:ts格式的片头
        :return:bool
        command: ffmpeg -i tmp_test_u5.mp4 -i tmp_test.mp4 -filter_complex '[0:0] [0:1] [1:0] [1:1] concat=n=2:v=1:a=1 [v] [a]' -map '[v]' -map '[a]' cc.mp4
        """
        inputs = []
        nums = ""
        for index in range(len(input_file)):
            inputs.append(" -i %s " % input_file[index])
            nums += "[{0}:0][{0}:1]".format(index)
        output_path = normpath(output_path)
        cmd = 'ffmpeg -y -loglevel error {} -max_muxing_queue_size 9999 -filter_complex "{} concat=n={}:v=1:a=1 [v] [a]" -map "[v]" -map "[a]" {}'.format(
            "".join(inputs),nums, len(inputs),output_path)
        return self._run(cmd)

    def resize_and_concat_and_water(self, head, video, water_image, font_image, output, width, last_start, x_value=0, height=480) -> bool:
        """
        :param video1:  片头视频
        :param video2:  内容视频
        :param last_start:  片尾文字水印起点
        :param x_value:  视频和文字水印的宽度差值， 可以负数
        :param water_image: 水印图片
        :param output:  输出文件
        :return:bool
        command: ffmpeg -y -i tmp_test_u5.mp4 -i tmp_test.mp4 -i water.png  -max_muxing_queue_size 9999  -filter_complex "[0:v][2:v]
        overlay=x=0:y=0[head];[1:v][2:v]overlay=x=0:y=0[content];[head][0:a][content][1:a]concat=n=2:v=1:a=1 [v][a]" -map '[v]' -map '[a]' xx.mp4
        """
        head = normpath(head)
        video = normpath(video)
        water_image = normpath(water_image)
        output = normpath(output)

        cmd = "ffmpeg -y -loglevel error -i {} -i {} -i {} -i {} -max_muxing_queue_size 9999 -filter_complex \"[0:v]scale={}:{},setdar={}/{}[headresize];[1:v]scale={}:{},setdar={}/{}[body];[body][3:v]overlay=x={}/2:enable='between(t,0,10)'[ten];[ten][3:v]overlay=x={}/2:enable='between(t,{},360000)'[resize];[headresize][2:v]overlay=x=0:y=0[head];[resize][2:v]overlay=x=0:y=0[content];[head][0:a][content][1:a]concat=n=2:v=1:a=1 [v][a]\" -map \"[v]\" -map \"[a]\" {}".format(
            head, video, water_image, font_image, width, height, width, height, width, height, width, height, x_value, x_value, last_start, output)
        return self._run(cmd)

    def make_webp_image(self, inputfile, output, workdir, size, start=0,  time=1) -> bool:
        """
        :param input:  视频
        :param output:  输出图片名
        :param workdir: 工作缓存目录， 避免交叉， 必须不一样
        :param start: 起点位置
        :param time: 多长时间
        ffmpeg -y -ss 100 -i dy_88dhp2xy_1.mp4 --lossless 0  -t {}  1.webp
        """
        output = join(normpath(workdir), output)
        log.info(output)
        cmd = "ffmpeg -y  -ss {} -loglevel error -max_muxing_queue_size 9999 -i {} -lossless 0 -s {} -t {}  {}".format(
            start, inputfile, size, time, output)
        return self._run(cmd)

    def merge_mp4s_and_make_webp(self, output,  *input) -> bool:
        import time
        """
        传进来多个输入合成一个输出 webp
        command: ffmpeg -y -i tmp_test_u5.mp4 -i tmp_test.mp4 -i water.png  -max_muxing_queue_size 9999  -filter_complex "[0:v][2:v]
        overlay=x=0:y=0[head];[1:v][2:v]overlay=x=0:y=0[content];[head][0:a][content][1:a]concat=n=2:v=1:a=1 [v][a]" -map '[v]' -map '[a]' xx.mp4
        """

        length = len(input)
        tmp_input = input[0]
        if length > 1:
            arr = []
            for inp in input:
                arr.append(" -i {} ".format(inp))
            tmp_mp4 = "{}.mp4".format(time.time())
            # 如果多个mp4 那个先合成一个
            vs = ""
            for i in range(length):
                vs += "[{}:v]".format(i)
            prefix = "ffmpeg -y -loglevel error  " + \
                " ".join(arr) + \
                "  -max_muxing_queue_size 9999  -filter_complex "
            suffix = '"{}concat=n={}:v=1 [v]" -map "[v]" {}'.format(
                vs, length, tmp_mp4)
            if not self._run(prefix + suffix):
                shell.remove_all(tmp_mp4)
                return False
            tmp_input = tmp_mp4
            # cmd = "ffmpeg -y -i {} -loglevel error -loop 0 -max_muxing_queue_size 9999  -lossless 0  {}".format(tmp_mp4, output)
            # ok = self._run(cmd)

        cmd = "ffmpeg -y -i {} -loglevel error -loop 0 -max_muxing_queue_size 9999 -filter:v fps=fps=20 -lossless 1 -preset  picture  -compression_level 6  {}".format(
            tmp_input, output)
        ok = self._run(cmd)
        if length > 1:
            shell.remove_all(tmp_input)
        return ok

    def check_video(self, input_file) -> bool:
        # 检查是否有视频画面和声音, 并且长度大于1秒的
        input_file = normpath(input_file)
        data = self.get_json_info(input_file)
        if data:
            try:
                valid = 0
                if int(float(data.format.duration)) < 1:
                    log.info("duration less than 1 second")
                    return False
                valid = 0
                for stream in data.streams:
                    if stream.codec_type == "audio":
                        log.info("have audio")
                        valid += 1
                        break
                for stream in data.streams:
                    if stream.codec_type == "video":
                        log.info("have video")
                        valid += 1
            except Exception as e:
                log.info(e)
                return False
            return valid >= 2
        return False

    def make_encrypt_tls(self, input_file, output, keyfile, time=2) -> bool:
        # 检查是否有视频声音
        input_file = normpath(input_file)
        #  -hls_segment_filename "{}%d.ts"
        cmd = 'ffmpeg  -loglevel error -i {} -hls_time {} -hls_key_info_file {} -hls_playlist_type vod -hls_list_size 0 -strict -2 -max_muxing_queue_size 9999 -f hls {}'.format(
            input_file, time, keyfile, output)
        return self._run(cmd)

    def make_tls(self, input_file, output, time=2):
        input_file = normpath(input_file)
        #  -hls_segment_filename "{}%d.ts"
        cmd = 'ffmpeg  -loglevel error -i {} -hls_time {} -hls_playlist_type vod -hls_list_size 0 -strict -2 -max_muxing_queue_size 9999 -f hls {}'.format(
            input_file, time, output)
        return self._run(cmd)

    def make_encrypt_tls_77xxx(self, input_file, output, keyfile, time=2, bitrate=0, fps=0) -> bool:
        # 检查是否有视频声音
        input_file = normpath(input_file)
        extend = ""
        if bitrate > 0:
            extend += " -b {}K ".format(bitrate)
        if fps > 0:
            extend += " -r {} ".format(fps)
        #  -hls_segment_filename "{}%d.ts"
        cmd = 'ffmpeg  -loglevel error -i {} -hls_time {} -force_key_frames "expr:gte(t,n_forced*1)" -hls_key_info_file {} {} -hls_playlist_type vod -hls_list_size 0 -strict -2 -max_muxing_queue_size 9999 -f hls {}'.format(
            input_file, time, keyfile, extend,  output)
        return self._run(cmd)

    def make_tls_77xxx(self, input_file, output, time=2, bitrate=0, fps=0):
        input_file = normpath(input_file)
        #  -hls_segment_filename "{}%d.ts"
        extend = ""
        if bitrate > 0:
            extend += " -b {}K ".format(bitrate)
        if fps > 0:
            extend += " -r {} ".format(fps)
        cmd = 'ffmpeg  -loglevel error -i {} -hls_time {} -force_key_frames "expr:gte(t,n_forced*1)" {} -hls_playlist_type vod -hls_list_size 0 -strict -2 -max_muxing_queue_size 9999 -f hls {}'.format(
            input_file, time, extend, output)
        return self._run(cmd)

    def rotate90(self, input_file, output) -> bool:
        cmd = 'ffmpeg -y -i {} -filter_complex "transpose=1" {}'.format(
            input_file, output)
        return self._run(cmd)

    def rotate180(self, input_file, output) -> bool:
        cmd = 'ffmpeg -y -i {} -filter_complex "[0:v]transpose=1[90];[90]transpose=1" {}'.format(
            input_file, output)
        return self._run(cmd)

    def rotate270(self, input_file, output) -> bool:
        cmd = 'ffmpeg -y -i {} -filter_complex "transpose=2" {}'.format(
            input_file, output)
        return self._run(cmd)


    def scale_video(self, format:FFmpegVideo) -> bool:
        rw, rh =  352, 198 # 缩放后的比例
        from common.calculate import reducewh
        w, h = ffmpeg.get_video_shape(format.input_file)
        nw, nh =reducewh(w, h, rw, rh)
        format.scale = "{}:{}".format(nw, nh)
        # 黑色填充
        format.pad = "{}:{}:{}:{}:black".format(rw, rh, (rw-nw)//2, (rh-nh)//2)

        cmd = 'ffmpeg -y -ss {start} -accurate_seek -t {step} -i {input_file}  -vf "scale={scale},pad={pad}" {output_file}'.format(**format.__dict__)
        return self._run(cmd)

    def make_hugo_video_auto(self, input_video, end, w, h, output, 
                              head, water_image, font_image, font_image_time, logo:Logo , font:Font, 
                             black_y, fontpath, start) -> bool:
        # input_video	string	视频路径
        # end	string	水印结束时间
        # w, h	int	水印边距位置
        # output	string	输出文件
        # head:  视频片头文件路径
        # 
        # water_image：  logo 水印图路径
        #  margin： logo水印位置
        
        # font_image： 广告图路径
        # font_image_time： 广告图的时间
        #  position：  文字水印位置
        # start： 视频开头时间
        # black_y:  head 填充视频的y位置
        #  font_water :  水印规则
        # 0 左上角，1 右上角，2 左下角，3右下角

        overlay = ""
        if logo.position == 0:
            overlay = "overlay=x={}:y={}".format(logo.padding, logo.padding)
        elif logo.position == 1:
            overlay = "overlay=x=main_w-overlay_w-{}:y={}".format(
                logo.padding, logo.padding)
        elif logo.position == 2:
            overlay = "overlay=x={}:y=main_h-overlay_h-{}".format(
                logo.padding, logo.padding)
        else:
            overlay = "overlay=x=main_w-overlay_w-{}:y=main_h-overlay_h-{}".format(
                logo.padding, logo.padding)

        font_position = ""
        if font.text:
            
            if font.position == 2:
                font_position = "h-line_h-{}".format(font.space)
            elif font.position == 1:
                font_position = "(h-line_h)/2"
            else:
                font_position = "{}".format(font.space)
        # 左到右的滚动文字， 滚动10秒， 间隔20秒
        inputcmd = ""

        #
        pos = 0
        sign = {}
        sign["input"] = "[{}:v]".format(pos)

        # 位置记录器
        pos += 1
        # concatcmd = '"'
        if head:
            # 片头
            sign["head"] = "[{}:v]".format(pos)
            inputcmd = " -i {}".format(head)
            pos += 1

        if font_image_time > 0 and font_image:
            # 文字水印
            sign["font"] = "[{}:v]".format(pos)
            inputcmd += " -i {}".format(font_image)
            pos += 1
        if water_image:
            # logo 水印
            sign["water"] = "[{}:v]".format(pos)
            inputcmd += " -i {}".format(water_image)
            pos += 1
        # 这是命令的前部分
        startcmd = 'ffmpeg -loglevel error -ss {} -to {} -i {} {}  -filter_complex "'.format(
            start, end, input_video, inputcmd)

        # 这是命令的后部分
        outcmd = ""
        if head:
            # 只有有片头视频才会这样处理
            outcmd = '" -map "[v]" -map "[a]" -max_muxing_queue_size 9999 -y {}'.format(
                output)
        else:
            outcmd = '" -max_muxing_queue_size 9999 -y {}'.format(output)

        #

        # 源视频缩放
        filtercmd = ["{}scale={}:{},setsar=1{}".format(
            sign["input"], w, h, "[resizemp4]"
        )]
        sign["input"] = "[resizemp4]"
        #
        if head:
            # 片头缩放
            filtercmd.append("{}scale={}:{},setsar=1,pad={}:{}:0:{}:black{}".format(
                sign["head"], w, h - black_y*2, w, h, black_y, "[resizehead]"
            ))
            sign["head"] = "[resizehead]"

        # 打文字图片水印， 是在源视频文件的基础上添加的
        if font_image_time > 0 and font_image:

            # 缩放文字水印
            filtercmd.append(
                "{}{}scale2ref=w=(iw*2/3):h=(ow/mdar)[fiamge][resize]".format(sign["font"], sign["input"]))
            sign["input"] = "[font_image]"
            filtercmd.append(
                "[resize][fiamge]overlay=x=(W/6):(H/4):enable='between(t,0,{})'{}".format(font_image_time, sign["input"]))

        # 文字水印
        if font.text:
            shadow = ""
            if font.shadow:
                shadow = "shadowx=2:shadowy=2:"

                # 如果有water_image 并且有文字水印
            filtercmd.append("{}drawtext=textfile={}:borderw={}:{}fontfile=font/bos.ttf:fontcolor={}:fontsize={}:y={}:x=w-(text_w+w)/{}*mod(t\,{}):enable=lt(mod(t\,{})\,{})[fontwater]".format(
                sign["input"],
                fontpath, font.border, shadow,
                font.color, font.size, font_position, font.interval,
                font.interval + font.scroll,
                font.interval, font.interval
            ))

            sign["input"] = "[fontwater]"
         # logo 水印
        if water_image:
            # 如果没有head， 那么位置就是1
            filtercmd.append("{}{}{}[addwater]".format(
                sign["input"], sign["water"], overlay))
            sign["input"] = "[addwater]"
        # 连接起来
        if head:
            filtercmd.append("{}[1:a]{}[0:a]concat=n=2:v=1:a=1[v][a]".format(
                sign["head"], sign["input"]))

        if filtercmd[-1][-1:] == "]" and filtercmd[-1][-3:] != "[a]":
            endindex = filtercmd[-1].rindex("[")
            filtercmd[-1] = filtercmd[-1][:endindex]
        cmd = startcmd + ";".join(filtercmd) + outcmd
        return self._run(cmd)


ffmpeg = FFmpeg()
