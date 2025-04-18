from PIL import ImageFont

# 加载自定义字体
font_path = r"E:\outline\msyh.ttc"
font_size = 24
custom_font = ImageFont.truetype(font_path, font_size)

# 计算文本大小
text = "你好，世界"
text_width, text_height = custom_font.getmask(text).size
print(text_height, text_width)