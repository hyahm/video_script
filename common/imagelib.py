# encoding=utf8

from PIL import Image, ImageFilter, ImageFile,ImageFont, ImageDraw, ImageEnhance
from common.log import log


class ImageHandle():
    """
    图片不存在就 raise
    """
    def __init__(self, image_path):
        # self.output = output
        self.image = Image.open(image_path)
        self.width, self.height = self.image.size
        self.format = self.image.format
        self.background_image = None
        self._err = None
        self.radius = 80
        self.need_radius = True
        self.new_image = None

    def get_width(self):
        return self.width

    def get_height(self):
        return self.height
    
    def set_radius(self, radius):
        """
        设置背景模糊半径
        """
        self.radius = radius
        self.need_radius = True


    def set_background_image(self, background_image):
        try:
            self.background_image = Image.open(background_image)
        except Exception as e:
            if len(e.args) > 0:
                self._err = str(e.args[0])
            else:
                self._err = e
        return False
    
    def new_background_image(self, width, height, mode='RGB', color=0):
        """
        创建新的背景图片
        """
        self.background_image = Image.new('RGB',(width, height), color)
        self.need_radius = False

    def get_thumb(self, output, width, height):
        # 创建一块幕布
        if not self.background_image:
            self.background_image = self.image
        if self.radius:
            self.background_image = self.background_image.filter(ImageFilter.GaussianBlur(radius=self.radius))
        self.background_image = self.background_image.resize((width, height))
        w, h = self._resize_by_auto(width, height)
        if w == 0:
            self.background_image.paste(self.new_image, (0, (height - h) // 2))
        else:
            self.background_image.paste(self.new_image, ((width - w) // 2, 0))

        try:
            try:
                self.background_image.save(output)
                return True
            except Exception as e:
                log.info(e)
                return False
        except:
            ImageFile.MAXBLOCK = w * h
            try:
                self.background_image.save(output)
                return True
            except Exception as e:
                log.error(e)
                return False 
        
    def _resize_by_auto(self, width, height):
        # 先根据宽度缩放图片比例
        # 等比放大缩小
        to_heigth = self.height * width // self.width
        if to_heigth >= height:
            # 再根据高度缩放图片比例
            to_width = self.width * height // self.height
            self.new_image = self.image.resize((to_width, height),Image.ANTIALIAS)
            self.height = height
            self.width = to_width
            return (to_width,0)
        else:
            self.new_image = self.image.resize((width, to_heigth),Image.ANTIALIAS)
            self.width = width
            self.height = to_heigth
            return (0, to_heigth)

    # 图片加上logo水印
    def paste_image(self, im, position, dst=""):
        try:
            pim = Image.open(im).convert('RGBA')
            pim = ImageEnhance.Color(pim).enhance(5)
            self.image.paste(pim, position, pim)
            if dst != "":
                self.image.show()
                # self.image.save(dst)
            return True
        except Exception as e:
            log.info(e)
            return False
    
    # 图片加上文字水印
    def paste_font(self, dst="", text="", position=(0,0), fontfile="font/bos.ttf", size=16, color="")-> bool: 
        # 传进来的color 必须是 16进制的   eg:  #FFF FFF  #79O8AF  79O8AF  
        from functional.color import color_to_rgb
        rgb, ok = color_to_rgb(color)
        if not ok:
            return False
        font=ImageFont.truetype(fontfile, size=int(size))
        draw = ImageDraw.Draw(self.image)
        draw.text(position, text, rgb, font=font)
        
        if dst != "":
            self.image.save(dst)
        return True

    def sharpen(self, out):
        # 锐化
        return self.image.filter(ImageFilter.SHARPEN).save(out)