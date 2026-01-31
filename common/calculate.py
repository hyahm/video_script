'''
Author: your name
Date: 2022-02-12 21:01:20
LastEditTime: 2022-03-04 22:55:13
LastEditors: your name
Description: 打开koroFileHeader查看配置 进行设置: https://github.com/OBKoro1/koro1FileHeader/wiki/%E9%85%8D%E7%BD%AE
FilePath: /hugo_scripts/common/calculate.py
'''
# 通过旧宽高和缩小后的新尺寸得出最佳新宽高

def reducewh(old_w, old_h, new_w, new_h) -> tuple:
    if old_w==0 or old_h==0 or new_w==0 or new_h==0:
        return (0,0)
    if old_w > new_w or old_h > new_h:
        # 任何一个旧尺寸大于新的，就要缩小
        w, h = 0,0
        # 比较谁缩得更小,那么以缩小比例更大的主
        if old_w / new_w >= old_h/new_h:
            w = new_w
            h = new_w*old_h//old_w
            if h % 2 != 0:
                h += 1
        else:
            h = new_h
            w = new_h*old_w//old_h
            if w % 2 != 0:
                w += 1
        return (w, h)
    # 如果比片子小，那么就事原尺寸
    return (old_w, old_h)