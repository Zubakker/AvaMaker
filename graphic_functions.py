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
    indent = 50 
    
    font_size = int(40 * ((IMG_WIDTH -2*indent)/width))
    height = int(height * ((IMG_WIDTH -2*indent)/width))
    # ---------- when the height is calculated we start drawing ---------------

    colored_text = Image.new("RGBA", (IMG_WIDTH, height + 1*indent), (0,0,0,0))
    uncolored_text = Image.new("RGBA", (IMG_WIDTH, height + 1*indent), (0,0,0,0))
    colored_outline = Image.new("RGBA", (IMG_WIDTH, height + 1*indent), (0,0,0,0))
    uncolored_outline = Image.new("RGBA", (IMG_WIDTH, height + 1*indent), (0,0,0,0))

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
        """
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
        """
        # --- colored letters ---
        if i in pattern:
            ctd.text((indent, 0), USERNAME[i], font=fnt, fill=bg_color, 
                    stroke_width=outline_thickness, stroke_fill=outline_bg
                    )
        # --- uncolored letters ---
        else:
            uctd.text((indent, 0), USERNAME[i], font=fnt, fill=fg_color,
                    stroke_width=outline_thickness, stroke_fill=outline_bg
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
    k = int(abs(255 * (brightness - 1)))
    line_height = int(line_height * img_height * 0.01)
    blur = int(img_height * blur * 0.01)
    thickness = int(img_height * thickness * 0.01)

    #b_color = (brightness, brightness, brightness, 255)
    b_color = (255, 255, 255, 255)

    blur_layer = Image.new("RGBA", (img_width, img_height), (0,0,0,0))
    white = Image.new("RGBA", (img_width, img_height), (0,0,0,255))
    #gray = Image.new("RGBA", (img_width, img_height), (brightness,brightness,brightness,255))
    # im.show() # <<<<<

    draw = ImageDraw.Draw(blur_layer)
    draw.line(((0, line_height), (img_width, line_height)), width=thickness, fill=b_color)
    blur_layer = blur_layer.filter(ImageFilter.BoxBlur(blur))
    blur_load = blur_layer.load()
    
    for i in range(img_width):
        for j in range(img_height):
             r, g, b, a = blur_load[i, j]
             r = int(k * (a/128))
             g = int(k * (a/128))
             b = int(k * (a/128))
             a = 0
             blur_load[i, j] = (r, g, b, a)

    if brightness > 1:
        result_c = ImageChops.add(bundle[0][0], blur_layer)
        result_uc = ImageChops.add(bundle[1][0], blur_layer)
    else:
        result_c = ImageChops.subtract(bundle[0][0], blur_layer)
        result_uc = ImageChops.subtract(bundle[1][0], blur_layer)

    return [[result_c, bundle[0][1]], [result_uc, bundle[1][1]]]



# add_parallel(image, brightness, offset)
#     ....
#     brightness is a floating number >= 0 that will change the brightness of the image, if the numberis greater than 1 the result will be brighter, otherwise the result will be darker 
#     offset defines the thickness of the parallel layer meassured in percents of the image height
def add_parallel(pair, colors, brightness, offset):
    img_width, img_height = pair[0].size
    offset = int(offset * img_height * 0.01)
    k = int((brightness -1) * 255)
    colors[0] = [int(brightness * x) for x in colors[0]]
    colors[1] = [int(brightness * x) for x in colors[1]]

    parallel_layer_c = Image.new("RGBA", (img_width, img_height), (0,0,0,0))
    parallel_layer_uc = Image.new("RGBA", (img_width, img_height), (0,0,0,0))

    par_c_load = parallel_layer_c.load()
    par_uc_load = parallel_layer_uc.load()
    img_c_load = pair[0].load()
    img_uc_load = pair[1].load()
    for x in range(img_width):
        for y in range(img_height-offset):
            for f in range(offset): 
                if img_c_load[x, y][3] != 0:
                    par_c_load[x, y+f] = tuple(colors[0] + [255])  
                if img_uc_load[x, y][3] != 0:
                    par_uc_load[x, y+f] = tuple(colors[1] + [255])  

    parallel_layer_c = Image.alpha_composite(parallel_layer_c, pair[0])
    parallel_layer_uc = Image.alpha_composite(parallel_layer_uc, pair[1])
    # parallel_layer.show()
    return parallel_layer_c, parallel_layer_uc 


def make_outline(image, width, color):
    h_width = int(width/2)
    img_width, img_height = image.size
    
    skeleton = image.filter(ImageFilter.FIND_EDGES)
    outlined = Image.new("RGBA", (img_width, img_height), (0,0,0,0))

    skeleton_load = skeleton.load()
    outlined_load = outlined.load()
    
    for x in range(width, img_width - width):
        for y in range(width, img_height - width):
            if skeleton_load[x, y][3]:
                for i in range(-width, width):
                    for j in range(-width, width):
                        outlined_load [x + i, y+j] = color


    result_img = Image.alpha_composite(outlined, image)
    return result_img
    # result_img.show()
