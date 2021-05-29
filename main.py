import argparse

from sys import argv, exit
from os import listdir
from random import choice
from PIL import Image, ImageFilter


import presets
try:
    from presets import *
except AttributeError as Err:
    print("AttributeError, it seems you have created some new preset files, please make sure to run: \n $ python presets/__modloader.py \n", Err)
    exit()
from colorschemes import colorschemes
from graphic_functions import generate_image, airbrush, add_parallel, make_outline


def choose_font(FONTNAME):
    directory = listdir('fonts')
    if not FONTNAME:
        if 'otf' not in ' '.join( directory ) and 'ttf' not in ' '.join( directory ):
            print("ERROR: no fonts found in the local 'fonts' directory")
            exit()
        FONTNAME = 'fonts/' + choice( directory ) 

    else:
        if FONTNAME not in ' '.join( directory ):
            print("ERROR: font '", FONTNAME, "' not found in the ./fonts directory", sep='')
            exit()
        for font in directory:
            if font.startswith(FONTNAME):
                FONTNAME = 'fonts/' + font
                break

    return FONTNAME


def choose_preset(PRESETNAME): # this function returnes a preset function, for a filename.py in the presets/ dir it returnes filename.main
    presets_list = list()
    directory = listdir('presets')
    PRESET = None
    for filename in directory: # browsing presets dir
        if filename.endswith('.py') and filename not in ('__init__.py', '__modloader.py'): # checking the file is a python program
            try:
                function = getattr(presets, filename[:-3]).main # we get the main() function from every file,
                                                                # the filename is sliced to get rid of .py extension
            except AttributeError as Err:                              
                print("AttributeError, it seems you have created some new preset files, please make sure to run: \n $ python presets/__modloader.py \n", Err)
                exit()
            presets_list.append(function)

    if not PRESETNAME:
        PRESET = choice( presets_list )
    else:
        for filename in directory:
            if filename.startswith(PRESETNAME):
                try:
                    PRESET = getattr(presets, filename[:-3]).main
                except AttributeError as Err:
                    print("AttributeError, it seems you have created some new preset files, please make sure to run: \n $ python presets/__modloader.py \n", Err)
                    exit()
        if not PRESET:
            print("ERROR: preset '", PRESETNAME, "' not found in the ./presets directory", sep='')
            exit()

    return PRESET


def choose_colors(COLORS, COLORSCHEME): # this function returns a tuple of two strings in 'RRGGBB' format for the primary and the secondary colors of the username
    if COLORS:
        return COLORS
    else:
        if COLORSCHEME == 'random':
            COLORSCHEME = choice(list(colorschemes))
        if COLORSCHEME not in list(colorschemes):
            print("ERROR: colorscheme '", COLORSCHEME, "' not found in ./colorschemes.py file", sep='')
            exit()
        COLORS = colorschemes[COLORSCHEME]
        return COLORS

def unpack_colors(colors):
    res = list()
    for color in colors:
        r = int(color[:2], 16)
        g = int(color[2:4], 16)
        b = int(color[4:], 16)
        res.append([r, g, b])
    return res



parser = argparse.ArgumentParser(
            description='This program creates colorful pictures with usernames'
            )
parser.add_argument('USERNAME', metavar='USERNAME', help="what text needs to be displayed")
parser.add_argument('-f', '--font', metavar='FONTNAME', type=str, dest='FONTNAME',
            help="specify the font you'd like to be used, see available fonts in ./fonts/ folder"
            )
parser.add_argument('-w', '--width', metavar='IMG_WIDTH', default=520, type=int, dest='IMG_WIDTH',
            help="specify width of the resulted image (height will be calculated automatically)"
            )
parser.add_argument('-p', '--preset', metavar='PRESETNAME', type=str, dest='PRESETNAME',
            help="specify the preset you'd like to be used, see available presets in ./presets/ folder"
            )
parser.add_argument('-c', '--colors', metavar=('COLOR1', 'COLOR2'), type=str, nargs=2, 
            dest='COLORS', help="specify the colors of the nickname in RRGGBB RRGGBB for two colors"
            )
parser.add_argument('-C', '--colorscheme', metavar='COLORNAME', type=str, default='wr', 
            dest='COLORSCHEME', help="specify the colorscheme you'd like to be used, see available colorschemes in the colorschemes.py file"
            )

args = parser.parse_args()
print(args)
USERNAME = args.USERNAME # the text we will show
IMG_WIDTH = args.IMG_WIDTH # the width of the resulted image, the height will be calculated automatically 
FONTNAME = args.FONTNAME # we will need font for the choose_font() function
PRESETNAME = args.PRESETNAME # the preset is a function that defines which letters will be colored 
COLORS = args.COLORS # we use two colors for the username coloration;
COLORSCHEME = args.COLORSCHEME # colorschemes are located in the ./colorschemes.py file 

FONT = choose_font(FONTNAME) # we choose a font if thuere is none and complete fontname if it is shortened (foofont -> foofont.ttf)
PRESET = choose_preset(PRESETNAME) # choose_preset returnes a preset function that can will be used to get the coloration of the username
RES_COLORS = unpack_colors(choose_colors(COLORS, COLORSCHEME)) # choose_colors returns a tuple of two 'RRGGBB' strings that define the colors of the username
# we also unpack them from ('RRGGBB', 'RRGGBB') format into [[R, G, B], [R, G, B]] format, where R,G,B are integers

OUTLINE_BRIGHTNESS = 1.4
OUTLINE_THICKNESS = 0.7

bundle = generate_image(FONT, USERNAME, IMG_WIDTH, PRESET, RES_COLORS, 
                  OUTLINE_BRIGHTNESS, OUTLINE_THICKNESS
                  )
bundle = airbrush(bundle, 0.7, 80, 10, 10)
bundle = airbrush(bundle, 1.3, 35, 10, 10)

image_c = Image.alpha_composite(bundle[0][1], bundle[0][0])
image_uc = Image.alpha_composite(bundle[1][1], bundle[1][0])
parallels = add_parallel((image_c, image_uc), RES_COLORS, 0.4, 7)

fin_one_c = Image.alpha_composite(parallels[0], bundle[0][0])
fin_one_uc = Image.alpha_composite(parallels[1], bundle[1][0])

fin_two_c = Image.alpha_composite(fin_one_c, bundle[0][1])
fin_two_uc = Image.alpha_composite(fin_one_uc, bundle[1][1])

fin_three = Image.alpha_composite(fin_two_c, fin_two_uc)
#parallel = Image.alpha_composite(parallel, image)
#parallel = Image.alpha_composite(parallel, outline)
fin_three.show()

nothing = Image.new("RGBA", fin_three.size, (0,0,0,0))

tone_dark = 0.8 
tone_light = 2.3 
width_dark = 8
width_light = 4
bg_color_dark = tuple([int(x*tone_dark) for x in RES_COLORS[0]] + [255])
bg_color_light = tuple([int(x*tone_light) for x in RES_COLORS[0]] + [255])
img = make_outline(fin_three, width_dark, bg_color_dark)
img = make_outline(img, width_light, bg_color_light)
fin_res = add_parallel((img, nothing), RES_COLORS, 0.7, 7)
fin_res = fin_res[0].filter(ImageFilter.BoxBlur(0.1))
fin_res.show()
'''
'''
    

# 6) общая внешняя обводка(толстая, тёмная)         7) новая общая обводка (толстая, светлая)    
# 8) ещё один параллельный слой
# 3) раскрашивание 4) искривление 

