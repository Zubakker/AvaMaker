from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageChops

# [V] 1) функция -- генерация картинки с текстом, но раскраска текста требует текста, поэтому
# логично их объекдинить в одну функцию, здесь будет создание текста по цвету, а цвет
# требует шаблона и ширины страницы, поэтому эта функция нормальная

# [V] 2) функция -- раскраска верха и низа цветами (по умолчанию тёмным и светлым)

# 3) функция -- обводка с цветом

# 4) функция -- параллельный слой 

# 5) функция -- искривление

# TODO надо поправить эту функцию красиво прописать
# outline_color is a float number >= 0 that describes how bright will the text outline be, if outline_color > 1 the outline will be brighter than the text, otherwise it will be darker
# outline_thickness is a float number meassured in percents of the image width
def generate_image(FONT, USERNAME, IMG_WIDTH, PRESET, RES_COLORS, outline_color, outline_thickness):
    fnt = ImageFont.truetype(FONT, 40)
    pattern = PRESET(USERNAME)[0] # PRESET is defined in the ./presets/ folder
    outline_thickness = int(outline_thickness * IMG_WIDTH * 0.01)

    # ---------- in this part we calculate the appropriate height and font size
    #            for our width, font and username length        ---------------
    text_layer = Image.new("RGBA", (IMG_WIDTH, 100), (0,0,0,0))
    
    text_draw = ImageDraw.Draw(text_layer)
    width, height = text_draw.textsize(USERNAME, font=fnt)
    indent = 10
    
    font_size = int(40 * ((IMG_WIDTH -3*indent)/width))
    height = int(height * ((IMG_WIDTH -3*indent)/width))
    # ---------- when the height is calculated we start drawing ---------------

    colored_text = Image.new("RGBA", (IMG_WIDTH, height + 3*indent), (0,0,0,0))
    uncolored_text = Image.new("RGBA", (IMG_WIDTH, height + 3*indent), (0,0,0,0))
    colored_outline = Image.new("RGBA", (IMG_WIDTH, height + 3*indent), (0,0,0,0))
    uncolored_outline = Image.new("RGBA", (IMG_WIDTH, height + 3*indent), (0,0,0,0))

    ctd = ImageDraw.Draw(colored_text)
    uctd = ImageDraw.Draw(uncolored_text)
    cod = ImageDraw.Draw(colored_outline)
    ucod = ImageDraw.Draw(uncolored_outline)

    fnt = ImageFont.truetype(FONT, font_size)

    bg_color = tuple(RES_COLORS[0] + [255])
    fg_color = tuple(RES_COLORS[1] + [255])
    k = int((outline_color - 1)*255)
    outline_bg = tuple([x + k for x in RES_COLORS[0]] + [255])
    outline_fg = tuple([x + k for x in RES_COLORS[1]] + [255])

    for i in range(len(USERNAME)): # coloring usernames according to the pattern
        letter_width, letter_height = text_draw.textsize(USERNAME[i], font=fnt)
        # --- colored letters ---
        if i in pattern:
            ctd.text((indent, 0), USERNAME[i], font=fnt, fill=bg_color)
            cod.text((indent-outline_thickness, -outline_thickness), 
                    USERNAME[i], font=fnt, fill=(0,0,0,0), 
                    stroke_width=outline_thickness, stroke_fill=outline_bg
                    )
        # --- uncolored letters ---
        else:
            uctd.text((indent, 0), USERNAME[i], font=fnt, fill=fg_color)
            ucod.text((indent-outline_thickness, -outline_thickness), 
                    USERNAME[i], font=fnt, fill=(0,0,0,0), 
                    stroke_width=outline_thickness, stroke_fill=outline_fg
                    )
        indent+= letter_width

    return [colored_text, colored_outline], [uncolored_text, uncolored_outline]



# airbrush(image, brightness, height, blur, thickness) 
#     the function adds a horizontal blurry line
# Arguments:
#     image is the PIL.Image object
#     brightness is a floating number >= 0 that will change the brightness of the image, if the numberis greater than 1 the result will be brighter, otherwise the result will be darker 
#     height is the vertical position for the hosizontal color strip meassured in precents
#     blur is the amount of blurriness, more = more blurry, less = more clear meassured in percents of the image height
#     thickness defines the size of the blurry line meassured in percents of the image height

def airbrush(bundle, brightness, line_height, blur, thickness): 
    img_width, img_height = bundle[0][0].size
    brightness = int(255 * (brightness - 1))
    line_height = int(line_height * img_height * 0.01)
    blur = int(img_height * blur * 0.01)
    thickness = int(img_height * thickness * 0.01)

    b_color = (255, 255, 255, 255)

    blur_layer = Image.new("RGBA", (img_width, img_height), (0,0,0,0))
    white = Image.new("RGBA", (img_width, img_height), (0,0,0,255))
    draw = ImageDraw.Draw(blur_layer)
    draw.line(((0, line_height), (img_width, line_height)), width=thickness, fill=b_color)
    blur_layer = blur_layer.filter(ImageFilter.BoxBlur(blur))

    shade_change_c = ImageChops.multiply(bundle[0][0], blur_layer)
    # shade_change_c.show()
    invis_shade_change_c = ImageChops.subtract(shade_change_c, white)
    result_c = ImageChops.subtract(bundle[0][0], invis_shade_change_c)

    shade_change_uc = ImageChops.multiply(bundle[1][0], blur_layer)
    invis_shade_change_uc = ImageChops.subtract(shade_change_uc, white)
    result_uc = ImageChops.subtract(bundle[1][0], invis_shade_change_uc)

    return [[result_c, bundle[0][1]], [result_uc, bundle[1][1]]]



# add_parallel(image, brightness, offset)
#     image is the PIL.Image object
#     brightness is a floating number >= 0 that will change the brightness of the image, if the numberis greater than 1 the result will be brighter, otherwise the result will be darker 
#     offset defines the thickness of the parallel layer meassured in percents of the image height
def add_parallel(image, brightness, offset):
    img_width, img_height = image.size
    offset = int(offset * img_height * 0.01)
    k = int((brightness -1) * 255)

    parallel_layer = Image.new("RGBA", (img_width, img_height), (0,0,0,0))
    parallel_layer.paste(image, (0, 0))

    img_load = image.load()
    par_load = parallel_layer.load()
    for x in range(img_width):
        for y in range(img_height):
            r, g, b, a = img_load[x, y]
            if par_load[x, y][3] != 0:
                par_load[x, y] = (r+k, g+k, b+k, 255)
    for x in range(img_width):
        for y in range(img_height-offset):
            for f in range(offset): 
                r, g, b, a = img_load[x, y]
                if par_load[x, y+f][3] == 0 and a != 0:
                    par_load[x, y+f] = (r+k, g+k, b+k, 255)  
                    # par_load[x, y+f] = (0, 0, 0, 255) 
#             if par_load[x, y][3] != 0:
 #                par_load[x, y] = (0, 200, 0, 255)

    parallel_layer = Image.alpha_composite(parallel_layer, image)
    # parallel_layer.show()
    return parallel_layer
