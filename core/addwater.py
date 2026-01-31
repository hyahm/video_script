from common.log import log
from request.status import UpdateStatus
from common.ffmpeg import ffmpeg
from common.shell import shell
from functional.images import resize_image
from lib.newrule import Rule
import time

# 打水印相关操作， 包括水印规则

class WaterMark():
    def __init__(self, rule: Rule):
        self.rule = rule
        # 最终视频的宽度和高度
        self.clean_list = []

    def clean(self) -> None:
        for path in self.clean_list:
            shell.remove_all(path)
        
    def add_water(self, video_path:str) -> bool:
        # resolve 对应的高度
        resolve_list = [480, 720, 1080]
        # 视频的高度
        _video_height = resolve_list[self.rule.resolve]
        # 视频缩放后的宽度和高度, 如果缩小的比例源视频还大， 那么已源视频大小为主
        width, height = ffmpeg.get_video_shape(video_path)
        if _video_height >= height:
            _video_height = height
        
        # 计算缩放后的视频大小， 保持是偶数
        _video_width = _video_height*width// height 
        if _video_width % 2 == 1:
                _video_width+=1
        
        # 字体是高度缩小20
        if self.rule.font.enable and self.rule.font.size <= 0:
            self.rule.font.size = _video_height//20
        
        # 计算head video 的大小
        head_path = ""
        _black_y = 0
        if self.rule.head.enable and self.rule.head.video_url:
            head_path = self.rule.head.get_video()
            if head_path == "": # 下载失败 todo
                return False
            self.clean_list.append(head_path)
            head_x, head_y = ffmpeg.get_video_shape(head_path)
            if head_x == 0:
                return False
            
            # 宽度与正片的宽度相等, 计算压缩后， 正片的正常, 只计算上下的间距， 左右的不管
            head_heigth = _video_width * head_y // head_x
            _black_y = (_video_height - head_heigth) // 2
            if _black_y < 0:
                _black_y = 0
        
        ad_image_path = ""
        if self.rule.ad.enable and self.rule.ad.url != "":
            ad_image_path = self.rule.ad.get_image()
            if not ad_image_path:
                return False
            self.clean_list.append(ad_image_path)
        # 裁剪logo图片
        logo_path = ""
        if self.rule.logo.enable and self.rule.logo.image_url != "":
            logo_path = self.rule.logo.get_image()
            
            if logo_path == "": # 下载失败 todo
                return False
            self.clean_list.append(logo_path)
            # 缩放logo图片
            water_width = resize_image(logo_path, 
            logo_path, _video_height, self.rule.logo.scale)
            if not water_width:
                log.error("create water image failed")
                return False
        video_length = ffmpeg.get_video_length(video_path)
        if self.rule.before >= video_length - self.rule.after:
            log.info("视频长度不够你切的")
            return False
        # 打水印

        _tmp_video = str(time.time()) + ".mp4"
        self.clean_list.append(_tmp_video)
        fontfile = self.rule.font.make_fontfile()
        if fontfile == "": # 下载失败 todo
            return False
        self.clean_list.append(fontfile)
        if not ffmpeg.make_hugo_video_auto(video_path,  
            video_length-self.rule.after, _video_width, 
            _video_height, _tmp_video, 
            head_path, logo_path,  ad_image_path, self.rule.ad.start, 
            self.rule.logo, self.rule.font, 
             _black_y, fontfile, self.rule.before):
            
            log.info("add water failed")
            return False
        shell.move_to(_tmp_video, video_path)
        return True
      
