# encoding=utf-8

def to_rgb(color):
    try:
        if color == 3:
            return (int(color[0], 16), int(color[1], 16),int(color[2], 16)), True
        else:
            return (int(color[0:2], 16), int(color[2:4], 16),int(color[4:], 16)), True
    except:
        return (), False
    
def color_to_rgb(color):
    if len(color) == 6 or len(color) == 3:
        return to_rgb(color)
    elif len(color) == 7 or len(color) == 4:
        color = color[1:]
        return to_rgb(color)
    else:
        return (), False