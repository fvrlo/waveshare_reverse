#!/usr/bin/python
# -*- coding:utf-8 -*-

import sys
import os
import psutil
import platform
picdir = os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))), 'pic')
libdir = os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))), 'lib')
if os.path.exists(libdir):
    sys.path.append(libdir)

import logging
import ntpath
import re
from contextlib import suppress
from waveshare_epd import epd2in13_V2
import time
from PIL import Image,ImageDraw,ImageFont,ImageChops,ImageOps

import traceback

logging.basicConfig(level=logging.DEBUG)


# General Variable Definitions
epd = epd2in13_V2.EPD() #my screen
image = Image.new('1', (epd.height, epd.width), 255)
draw = ImageDraw.Draw(image)
nc = 'nc'
maxList = [3,5,4]
defList = [1,5,4]
h = 122
w = 250
font15 = ImageFont.truetype(os.path.join(picdir, 'Font.ttc'), 15)
font24 = ImageFont.truetype(os.path.join(picdir, 'Font.ttc'), 24)
fontBIG = ImageFont.truetype(os.path.join(picdir, 'Font.ttc'), 122)





def fullClear():
    # Clear for startup, defines fullscreen updates and clears
    epd.init(epd.FULL_UPDATE)
    epd.Clear(0xFF)
def miniClear():
    # Clear for startup, defines fullscreen updates and clears
    global image, draw
    image = Image.new('1', (epd.height, epd.width), 255)
    draw = ImageDraw.Draw(image)
def display(tim=2):
    #Display and clear afterwards (if you want)
    global image, draw
    epd.display(epd.getbuffer(image))
    time.sleep(tim)
def logTranscode(rL):
    if '1' in rL[1]:
        if '3' in rL[1]:
            if '4' in rL[1]:
               logging.info(" Image has missing arguments, please fix.")
               exit()
            logging.info(" Image variables are too large, please fix.")
            exit()
        logging.info(" Image variables are not numeric. Please use defined options.")
        exit()
def imgVar(uL):
    rL = []
    for i in range(3):
        try:
            if uL[i].isnumeric() != True:
                seq_type = type(uL[i])
                seq_type().join(filter(seq_type.isdigit, uL[i]))
                uL[i] = int(uL[i])
                rL.append('1')
        except: pass;
        try:
            if int(uL[i]) <= maxList[i]:
                rL.append('2')
                continue
            else:
                rL.append('3')
                uL[i] = int(defList[i])
        except:
            rL.append('4')
            uL[i] = uL.append(int(defList[i]))
    logTranscode(rL)
    return uL
def imgPrep(img,*varia):
    #Filter Modules
    def s_scale(img):
        img.resize((w,h),resample=1)
    def s_fit(img):
        ImageOps.fit(img,(w,h),3,1,(0.5,0.5))
    def v_autoc(img):
        ImageOps.autocontrast(img)
    def v_invert(img):
        ImageChops.invert(img)
    def v_mirror(img):
        ImageChops.mirror(img)
    def v_flip(img):
        ImageChops.flip(img)
    def d_median(img):
        img.quantize(2,0,0,0,1)
    def d_maxco(img):
        img.quantize(2,1,0,0,1)
    def d_fasto(img):
        img.quantize(2,2,0,0,1)
    def d_libqu(img):
        img.quantize(2,3,0,0,1)
            # General image prep operation.
            # Open image, force RGB, fix varia.
            # If you want alpha passing, use imgPrepAlpha
            # Image will then need a dither of some sort and optionally effects followed by a scaler.
    img = Image.open(os.path.join(picdir,img))
    img = img.convert('RGB')
    useList=imgVar(list(str(varia[0])))
    
            # First option: Scale or fit.
            # 1 for scale, 2 for fit, and 3 for passthrough, assuming image is already proper size
            #print(useList[0])
    if useList[0] == 1 : s_scale(img)
    if useList[0] == 2 : s_fit(img)
    if useList[0] == 3 : pass
    
            # Second option: filter.
            # 1 for autocontrast, forcing 0-127 to 0 and 128-255 to 1
            # 2 for inverting the color
            # 3 for mirroring l/r
            # 4 for flipping t/b
            # 5 for passthrough, no filters.
            #rint(useList[1])
    if useList[1] == 1 : v_autoc(img)
    if useList[1] == 2 : v_invert(img)
    if useList[1] == 3 : v_mirror(img)
    if useList[1] == 4 : v_flip(img)
    if useList[1] == 5 : pass
    
            # Third option: dithering.
            # By default, 4 should be chosen for quality, but 1 is quicker and dirtier.
            # If filter is set to autocontrast, this is skipped.
            # 1 for median cut
            # 2 for maxcoverage
            # 3 for fastoctree
            # 4 for libimagequant
            #print(useList[2])
    if useList[1] != 1:
        if useList[2] == 1 : d_median(img)
        if useList[2] == 2 : d_maxco(img)
        if useList[2] == 3 : d_fasto(img)
        if useList[2] == 4 or useList[2] != range(1,4): d_libqu(img)
    #print(img)
    #img.convert("1")
    return img
def testOut():
    fullClear()
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
    draw.text((120, 60), 'pepega', font = font15, fill = 0)
    draw.text((110, 90), u'微雪电子', font = font24, fill = 0)

# You always start with draw defined, and image set to a blank canvas
# Display will always pull from the buffer 'image' unless defined otherwise.
# Top left is 0,0, gold foil is leftside

mode = "matt"
try:
    if mode == "matt":
        epd.init(epd.FULL_UPDATE)
        #image = imgPrep('fullcolorfullres.bmp','154')
        #display(1)
        #miniClear()

        #draw.text((0, 0), 'pepega', font = fontBIG, fill = 0)
        #display(1)
        #miniClear()

        #image = imgPrep('imgfgg.png','111')
        #display(1)
        #miniClear()
    
        paste = imgPrep('comm.png','154')
        image.paste(paste, (50,0))    
        display(2)
        fullClear()
    if mode == "partialTest":
        #partial update
        #logging.info("4.show time...")
        #fullClear()
        time_image = Image.new('1', (epd.height, epd.width), 255)
        time_draw = ImageDraw.Draw(time_image)
    
        epd.init(epd.FULL_UPDATE)
        epd.displayPartBaseImage(epd.getbuffer(time_image))
    
        epd.init(epd.PART_UPDATE)
        num = 0
        while (True):
            paste = imgPrep('comm.png','154')
            time_image.paste(paste, (0,0))
            time_draw.rectangle((120, 80, 220, 105), fill = 255)
            time_draw.rectangle((180, 20, 240, 40), fill = 255)
            time_draw.text((120, 80), time.strftime('%H:%M:%S'), font = font24, fill = 0)
            time_draw.text((180, 20), str(psutil.cpu_percent(interval=None)) , font = font24, fill = 0)
            epd.displayPartial(epd.getbuffer(time_image))
            num = num + 1
            if(num == 100):
                break
    
    logging.info("Goto Sleep...")
    epd.sleep()
        
except IOError as e:
    logging.info(e)
    
except KeyboardInterrupt:    
    logging.info("ctrl + c:")
    logging.info("Clear...")
    epd.init(epd.FULL_UPDATE)
    epd.Clear(0xFF)
    epd2in13_V2.epdconfig.module_exit()
    exit()
