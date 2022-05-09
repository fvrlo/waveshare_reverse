import epdConfig
import sys
for vari in [x for x in dir(epdConfig) if x.startswith('EPD_') or x.startswith('pic_')]:
    if vari == int:
        variInt = int(vari)
        exec(vari + " = 4"), exec(vari + " = " + variInt)
    else:
        exec(vari + " = 4"), exec(vari + " = " + vari)
for func in [x for x in dir(epdConfig) if not x.startswith('_')]:
    setattr(sys.modules[__name__], func, getattr(epdConfig, func))
#startup ^

import os
import time
import psutil, platform, re
from PIL import Image, ImageDraw, ImageFont, ImageChops, ImageOps
#import ^

flipZ = 1  #    1 to rotate (screen on bottom), 0 to stay
def startup():
    try: flipZ = flipZ
    except NameError: flipZ = 0
    image = EPD_image
    draw = EPD_draw
    init(0)
    Clear(0xFF)
    image = Image.new('1', (122, 250), 255)
    draw = ImageDraw.Draw(image)
    if(flipZ == 1):
        setFlip(1)
    else:
        setFlip(0)

class premades():
    def testOut():
        image = Image.new('1', (122, 250), 255)
        draw = ImageDraw.Draw(image)
        draw.rectangle([(0,0),(50,50)],outline = 0)
        draw.rectangle([(55,0),(100,50)],fill = 0)
        draw.line([(0,0),(50,50)], fill = 0,width = 1)
        draw.line([(0,50),(50,0)], fill = 0,width = 1)
        draw.chord((10, 60, 50, 100), 0, 360, fill = 0)
        draw.ellipse((55, 60, 95, 100), outline = 0)
        draw.pieslice((55, 60, 95, 100), 90, 180, outline = 0)
        draw.pieslice((55, 60, 95, 100), 270, 360, fill = 0)
        draw.polygon([(110,0),(110,50),(150,25)],outline = 0)
        draw.polygon([(190,0),(190,50),(150,25)],fill = 0)
        draw.text((120, 60), 'pepega', font = pic_font15, fill = 0)
        draw.text((110, 90), u'微雪电子', font = pic_font24, fill = 0)
        display(getbuffer(image))
        time.sleep(2)

    def fcfr():
        image = run('fullcolorfullres.bmp',1,5,4)
        display(getbuffer(image))
        time.sleep(2)

    def fcfrVar(v1,v2,v3):
        image = run('fullcolorfullres.bmp',v1,v2,v3)
        display(getbuffer(image))
        time.sleep(2)

    def pepegeFont():
        image = Image.new('1', (122, 250), 255)
        draw.text((0, 0), 'pepega', font = fontBIG, fill = 0)
        display(getbuffer(image))
        time.sleep(2)

    def imgfgg():
        image = run('imgfgg.png',1,1,1)
        display(getbuffer(image))
        time.sleep(2)

    def comm():
        image = run('comm.png',1,5,4)
        image.paste(image, (50,0))
        display(getbuffer(image))
        time.sleep(2)


try:
    startup()
    #displayIgnoreOther(bufferXO())
    getbuffer(image = run('fullcolorfullres.bmp',1,5,4))
    sleep()

except IOError as e:
    print('IOError shutdown: ' + str(e))

except KeyboardInterrupt as e:
    print('Keyboard Shutdown: ' + str(e))
    init(0)
    Clear(0xFF)
    module_exit()