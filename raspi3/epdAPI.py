import os, sys, time, threading, inspect, psutil, platform, re, spidev, traceback
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageChops, ImageOps
import RPi.GPIO as GPIO
from pathlib import Path
SPI = spidev.SpiDev()
import binascii

picdir = Path(__file__).with_stem('pic').with_suffix('')
font = os.path.join(picdir, 'Font.ttc')
font1 = ImageFont.truetype(font, 15)
font2 = ImageFont.truetype(font, 24)
font3 = ImageFont.truetype(font, 122)

EPD_WIDTH = 122
EPD_HEIGHT = 250
EPD_RST_PIN = 17
EPD_DC_PIN = 25
EPD_CS_PIN = 8
EPD_BUSY_PIN = 24
EPD_FULL_UPDATE = 0
EPD_PART_UPDATE = 1

def preset_outputs(option):
    def oDemo1():
        image = Image.new('1', (250, 122), 255)
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
        draw.text((120, 60), 'e-Paper demo', font = font1, fill = 0)
        draw.text((110, 90), u'微雪电子', font = font2, fill = 0)
        display(image,2,0)
    def oDemo2():
        image = Image.new('1', (250, 122), 255)
        draw = ImageDraw.Draw(image)
        display(prep('2in13.bmp',3,4,1),2,0)
    def oDemo3():
        blank = Image.new('1', (250, 122), 255)
        onTop = prep('100x100.bmp',3,4,1)
        Image.Image.paste(blank, onTop, (2,2))
        display(blank,3,0)
    def oDemo4():
        blank = Image.new('1', (250, 122), 255)
        onTop = prep('100x100.bmp',3,4,1)
        Image.Image.paste(blank, onTop, (2,2))
        display(blank,5,1)
    def sampleImage():
        display(prep('fullcolorfullres.bmp',1,5,4),2,0)
    def sampleText():
        image = Image.new('1', (250, 122), 255)
        draw = ImageDraw.Draw(image)
        draw.text((0, 0), 'pepega', font = font2, fill = 0)
        display(image,2,0)
    def sampleScale():
        display(prep('imgfgg.png',1,1,1),2,0)
    def samplePaste():
        image = prep('comm.png',1,5,4)
        image.paste(image, (50,0))
        display(image,2,0)
    def oDemo():
        oDemo1()
        oDemo2()
        oDemo3()
        oDemo4()
    def gradi():
        image = Image.linear_gradient('L')
        display(prep(image,1,4,4),2,0)
    pattern = re.compile('[\W_]+', re.UNICODE)
    pattern.sub('', option)
    for x in (x for x in dir() if x != ('option' or 'x')):
        pattern.sub('', x)
        if(str(x) == option):
            exec((x + '()'))

def clear(color):
    send_command(0x24)
    for j in range(0, EPD_HEIGHT):
        for i in range(0, 16):
            send_data(color)
    send_command(0x22)
    send_data(0xC7)
    send_command(0x20)
    while(GPIO.input(EPD_BUSY_PIN) == 1): time.sleep(0.1)

def startup(*imgvar):
    if imgvar[0] == 1:
        display.flip = 1
    elif imgvar[0] == 0:
        display.flip = 0
    init(EPD_FULL_UPDATE)
    clear(0xFF)

def shutdown():
    clear(0xFF)
    send_command(0x22) #POWER OFF
    send_data(0xC3)
    send_command(0x20)
    
    SPI.close()
    GPIO.output(EPD_RST_PIN, 0)
    GPIO.output(EPD_DC_PIN, 0)
    GPIO.cleanup([EPD_RST_PIN, EPD_DC_PIN, EPD_CS_PIN, EPD_BUSY_PIN])

def sleep(*clr):
    try:
        if(clr == 0xFF): clear(clr)
    except: pass
    send_command(0x10) #enter deep sleep
    send_data(0x03)
    time.sleep(2)
    SPI.close()
    GPIO.output(EPD_RST_PIN, 0)
    GPIO.output(EPD_DC_PIN, 0)
    GPIO.cleanup([EPD_RST_PIN, EPD_DC_PIN, EPD_CS_PIN, EPD_BUSY_PIN])

def init(update):
    try:
        if(init.mod == 0): pass
    except:
        init.mod = 0
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)
        GPIO.setup(EPD_RST_PIN, GPIO.OUT)
        GPIO.setup(EPD_DC_PIN, GPIO.OUT)
        GPIO.setup(EPD_CS_PIN, GPIO.OUT)
        GPIO.setup(EPD_BUSY_PIN, GPIO.IN)
        # SPI device, bus = 0, device = 0
        SPI.open(0, 0)
        SPI.max_speed_hz = 4000000
        SPI.mode = 0b00
    
    # EPD hardware init start
    GPIO.output(EPD_RST_PIN, 1)
    time.sleep(200 / 1000)
    GPIO.output(EPD_RST_PIN, 0)
    time.sleep(5 / 1000)
    GPIO.output(EPD_RST_PIN, 1)
    time.sleep(200 / 1000)
    
    if(update == EPD_FULL_UPDATE):
        while(GPIO.input(EPD_BUSY_PIN) == 1): time.sleep(0.1)
        send_command(0x12) # soft reset
        while(GPIO.input(EPD_BUSY_PIN) == 1): time.sleep(0.1)
        send_command(0x74) #set analog block control
        send_data(0x54)
        send_command(0x7E) #set digital block control
        send_data(0x3B)
        send_command(0x01) #Driver output control
        send_data(0xF9)
        send_data(0x00)
        send_data(0x00)
        send_command(0x11) #data entry mode
        send_data(0x01)
        send_command(0x44) #set Ram-X address start/end position
        send_data(0x00)
        send_data(0x0F)    #0x0C-->(15+1)*8=128
        send_command(0x45) #set Ram-Y address start/end position
        send_data(0xF9)   #0xF9-->(249+1)=250
        send_data(0x00)
        send_data(0x00)
        send_data(0x00)
        send_command(0x3C) #BorderWavefrom
        send_data(0x03)
        send_command(0x2C)     #VCOM Voltage
        send_data(0x55)    #
        send_command(0x03)
        send_data(0x15)
        send_command(0x04) #
        send_data(0x41)
        send_data(0xA8)
        send_data(0x32)
        send_command(0x3A)     #Dummy Line
        send_data(0x30)
        send_command(0x3B)     #Gate time
        send_data(0x0A)
        send_command(0x32)
        EPD_LUT_FULL = [0x80,0x60,0x40] + [0x00]*4 + [0x10,0x60,0x20,0x00,0x00,0x00,0x00,0x80,0x60,0x40,0x00,0x00,0x00,0x00,0x10,0x60,0x20,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x03,0x03,0x00,0x00,0x02,0x09,0x09,0x00,0x00,0x02,0x03,0x03,0x00,0x00,0x02,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00]
        for count in range(70):
            send_data(EPD_LUT_FULL[count])
        send_command(0x4E)   # set RAM x address count to 0
        send_data(0x00)
        send_command(0x4F)   # set RAM y address count to 0X127
        send_data(0xF9)
        send_data(0x00)
        while(GPIO.input(EPD_BUSY_PIN) == 1): time.sleep(0.1)
    else:
        send_command(0x2C)     #VCOM Voltage
        send_data(0x26)
        while(GPIO.input(EPD_BUSY_PIN) == 1): time.sleep(0.1)
        send_command(0x32)
        EPD_LUT_PART = [0x00]*7 + [0x80] + [0x00]*6 + [0x40] + [0x00]*20 + [0x0A] + [0x00]*34
        for count in range(70):
            send_data(EPD_LUT_PART[count])
        send_command(0x37)
        send_data(0x00)
        send_data(0x00)
        send_data(0x00)
        send_data(0x00)
        send_data(0x40)
        send_data(0x00)
        send_data(0x00)
        send_command(0x22)
        send_data(0xC0)
        send_command(0x20)
        while(GPIO.input(EPD_BUSY_PIN) == 1): time.sleep(0.1)
        send_command(0x3C) #BorderWavefrom
        send_data(0x01)
    return 0

def send_command(command):
    GPIO.output(EPD_DC_PIN, 0)
    GPIO.output(EPD_CS_PIN, 0)
    SPI.writebytes([command])
    GPIO.output(EPD_CS_PIN, 1)

def send_data(data):
    GPIO.output(EPD_DC_PIN, 1)
    GPIO.output(EPD_CS_PIN, 0)
    SPI.writebytes([data])
    GPIO.output(EPD_CS_PIN, 1)

# Image processing functions
def prep(imgvar, *outL):
    if(type(outL[0]) != int): outL = outL[0]
    if(len(outL) == 0): outL = [1,4,4]
    elif(len(outL) == 1): outL = [outL[0],4,4]
    elif(len(outL) == 2): outL = [outL[0],outL[1],4]
    try:
        img = Image.open(os.path.join(picdir,str(imgvar))).convert('RGB')
    except:
        img = imgvar
    # Sizing: (1)Scale, (2)Fit, (3)Passthrough
    if outL[0] == 1 : img = img.resize((250,122),resample=1)
    if outL[0] == 2 : img = ImageOps.fit(img,(250,122),3,1,(0.5,0.5))
    if outL[0] == 3 : pass
    # Filters: (1)Invert, (2)Mirror Horizontally, (3)Flip Vertically, (4)Passthrough
    if outL[1] == 1 : img = ImageOps.invert(img)
    if outL[1] == 2 : img = ImageOps.mirror(img)
    if outL[1] == 3 : img = ImageOps.flip(img)
    if outL[1] == 4 : pass
    # Dither: (1)Median, (2)Maximum, (3)Fast-Octree, (4)Quantize
    if outL[2] == 1 : img = img.quantize(2,0,0,0,1)
    if outL[2] == 2 : img = img.quantize(2,1,0,0,1)
    if outL[2] == 3 : img = img.quantize(2,2,0,0,1)
    if outL[2] == 4 : img = img.quantize(2,3,0,0,1)
    img = img.convert('1')
    return img

class RepeatedTimer(object):
    def __init__(self, interval, function, *args, **kwargs):
        self._timer = None
        self.interval = interval
        self.function = function
        self.args = args
        self.kwargs = kwargs
        self.is_running = False
        self.next_call = time.time()
        self.start()

    def _run(self):
        self.is_running = False
        self.start()
        self.function(*self.args, **self.kwargs)

    def start(self):
        if not self.is_running:
            self.next_call += self.interval
            self._timer = threading.Timer(self.next_call - time.time(), self._run)
            self._timer.start()
            self.is_running = True

    def stop(self):
        self._timer.cancel()
        self.is_running = False

# width: 122
# height: 250 (32 if buffer)
# buffer changes height
# height in the code is really width
#
# if pixels[x, y] == 0:
#     x = imwidth - x
#     buf[int(x / 8) + y * 32] &= ~(0x80 >> (x % 8))
# buf[pos] &= cycle
# Cycle: x cycles through 128>64>32>16>8>4>2>1, repeats. Gotta be the bit marks in the byte.
# pos: basically is one number for each chunk, while y is 0, x will be 0-31
# (32 starts when x = 256 and y = 0, aka out of bounds, so it's the next line)
# row 1: pos = 0-31
# row 2: pos = 32-64
# etc
# each new value for buffer is just the 8 pixels in binary, sent as hex.
# does seem like it goes backwards through x
# starts at x = 250
# so 250, 249, and 248 seemingly get the whole bit to themselves
# tilde flips the bits, making the operation bitwise
# starts as 11111111
# 
#
#
# if the pixel is 0, the binary flips to be 0 (aka pixel 0-7 is 0, buffer is 00000000
# example: bit 31 is only the three digits 250, 249, 248
# their byte is 00011111
# 248,249,250,null x5
# directionally the whole image is stored in buffer top right to bottom left, aka a vertical axis flip
#
#EPD_WIDTH = 122
#EPD_HEIGHT  = 250




def conv(data):
    out = format(data, '08b')
    return list(out)


def bufferTrans(image):
    imgArray = np.rot90(np.array(image,dtype='short'),2)
    bufArray = np.full((16, 250), 0xFF,dtype='short')
    for x,y in np.ndindex(imgArray.shape):
        if imgArray[x, y] == 0:
            bufArray[int((122 - x) / 8), y] &= ~(0x80 >> x % 8)
    return bufArray






def display(image,timerLength,refresh=0):
    try: flip = display.flip
    except: flip = 0
    if(refresh == 0):
        if(flip == 1):
            image = image.rotate(180)
        buf = [0xFF] * 4000
        init(EPD_FULL_UPDATE)
        send_command(0x24)
        imageOut = bufferTrans(image)
        imx, imy = imageOut.shape
        lx = []
        ly = []
        bufArray = np.full((250, 16), 0,dtype=object)
        for i, j in np.ndindex((250,16)):
            send_data(int(imageOut[j, i]))
            bufArray[i,j] = int(imageOut[j,i])
            lx.append(int(imageOut[j, i]))
        for x in range(len(lx)):
            ly = ly + conv(lx[x])
        for x in range(len(ly)):
            ly[x] = int(ly[x])
        print(ly[70])
        print(len(ly))
        lx = np.array(lx)
        oup = Image.frombytes('1',(128,250),imageOut)
        oup2 = Image.frombytes('1',(250,128),imageOut)
        oup2.save('out2.png')
        oup.save('out.png')
        send_command(0x22)
        send_data(0xC7)
        send_command(0x20)
        while(GPIO.input(EPD_BUSY_PIN) == 1): time.sleep(0.1)
    
    if(refresh == 1):
        if(flip == 1):
            image = image.rotate(180)
        buf = [0xFF] * 4000
        init(EPD_FULL_UPDATE)
        send_command(0x24)
        imwidth, imheight = image.size
        pixels = image.load()
        if(imwidth == 122 and imheight == 250): typr = 'vert'
        else: typr = 'horiz'
        for x, y in np.ndindex((imwidth,imheight)):
            if pixels[x, y] == 0:
                if(typr == 'vert'): buf[int((imwidth - x) / 8) + y * 16] &= ~(0x80 >> ((imwidth - x) % 8))
                elif(typr == 'horiz'): buf[int(y / 8) + (imwidth - (250 - x - 1) - 1)*16] &= ~(0x80 >> (y % 8))
        imageOut = buf
        for j,i in np.ndindex((250,16)):
            send_data(imageOut[i + j * 16])
        send_command(0x26)
        for j,i in np.ndindex((250,16)):
            send_data(imageOut[i + j * 16])
        send_command(0x22)
        send_data(0xC7)
        send_command(0x20)
        while(GPIO.input(EPD_BUSY_PIN) == 1): time.sleep(0.1)
        init(EPD_PART_UPDATE)
        draw = ImageDraw.Draw(image)
        num = 0
        while (True):
            draw.rectangle((120, 80, 220, 105), fill = 255)
            draw.text((120, 80), time.strftime('%H:%M:%S'), font = font2, fill = 0)
            imwidth, imheight = image.size
            pixels = image.load()
            if(imwidth == 122 and imheight == 250): typr = 'vert'
            else: typr = 'horiz'
            buf = [0xFF] * 4000
            for x, y in np.ndindex((imwidth,imheight)):
                if pixels[x, y] == 0:
                    if(typr == 'vert'): buf[int((imwidth - x) / 8) + y * 16] &= ~(0x80 >> ((imwidth - x) % 8))
                    elif(typr == 'horiz'): buf[int(y / 8) + (imwidth - (250 - x - 1) - 1)*16] &= ~(0x80 >> (y % 8))
            imageOut = buf
            send_command(0x24)
            for j,i in np.ndindex((250,16)):
                send_data(imageOut[i + j * 16])
            send_command(0x26)
            for j,i in np.ndindex((250,16)):
                send_data(~imageOut[i + j * 16])
            send_command(0x22)
            send_data(0x0c)
            send_command(0x20)
            num = num + 1
            if(num == timerLength):
                break
        #rt = RepeatedTimer(1, party)
        #time.sleep(timerLength + 0.4)
        #rt.stop()


# epdAPI.startup(option)
# 1 to rotate processed images (screen on bottom), 0 to stay
epdAPI.startup(1)
#epdAPI.preset_outputs('oDemo3')
#epdAPI.preset_outputs('sampleImage')
#epdAPI.preset_outputs('oDemo3')
#epdAPI.preset_outputs('sampleImage')
#epdAPI.preset_outputs('oDemo3')
epdAPI.preset_outputs('sampleImage')
epdAPI.sleep(0xFF)
#epdAPI.shutdown()
