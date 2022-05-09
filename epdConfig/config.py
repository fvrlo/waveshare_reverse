import os
import sys
import time
import numpy as np
import psutil, platform, re
from PIL import Image, ImageDraw, ImageFont, ImageChops, ImageOps
from .varia import *

maindir = os.path.abspath(os.path.join(os.path.dirname(os.path.realpath(__file__)), '..'))
picdir = maindir + '/pic'

def digital_write(pin, value):
    GPIO.output(pin, value)

def digital_read(pin):
    return GPIO.input(pin)

def delay_ms(delaytime):
    time.sleep(delaytime / 1000.0)

def spi_writebyte(data):
    SPI.writebytes(data)

def spi_writebyte2(data):
    SPI.writebytes2(data)

def module_init():
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
    return 0

def module_exit():
    SPI.close()
    GPIO.output(EPD_RST_PIN, 0)
    GPIO.output(EPD_DC_PIN, 0)
    GPIO.cleanup([EPD_RST_PIN, EPD_DC_PIN, EPD_CS_PIN, EPD_BUSY_PIN])

def imgArg(*ruL):
    uL = list(ruL)
    length = len(uL)
    outL = []
    if length == 0:
        outL.append(1)
        outL.append(5)
        outL.append(4)
    elif length == 1:
        outL.append(uL[0])
        outL.append(5)
        outL.append(4)
    elif(length == 2) and (uL[1] != 1):
        outL.append(4)
    elif(length == 2) and (uL[1] == 1):
        outL.append(5)
    return outL

def setFlip(var):
    setFlip.flip = var

def autoFill(*var):
    if(type(var) != int): var = var[0]
    if(len(var) == 0): var = [1,4,4]
    elif(len(var) == 1): var = [var[0],4,4]
    elif(len(var) == 2): var = [var[0],var[1],4]
    return var

def run(imgvar, *varia):
    # Prepare variables
    try: zFlip = setFlip.flip
    except: zFlip = 0
    img = Image.open(os.path.join(picdir,str(imgvar))).convert('RGB')
    useList = autoFill(varia)
    # Sizing: (1)Scale, (2)Fit, (3)Passthrough
    if useList[0] == 1 : img = img.resize((250,122),resample=1)
    if useList[0] == 2 : img = ImageOps.fit(img,(250,122),3,1,(0.5,0.5))
    if useList[0] == 3 : pass
    # Filters: (1)Auto-contrast, (2)Invert, (3)Mirror Horizontally, (4)Flip Vertically, (5)Passthrough
    if useList[1] == 1 : img = ImageOps.invert(img)
    if useList[1] == 2 : img = ImageOps.mirror(img)
    if useList[1] == 3 : img = ImageOps.flip(img)
    if useList[1] == 4 : pass
    # Dither: (1)Median, (2)Maximum, (3)Fast-Octree, (4)Quantize
    if useList[2] == 1 : img = img.quantize(2,0,0,0,1)
    if useList[2] == 2 : img = img.quantize(2,1,0,0,1)
    if useList[2] == 3 : img = img.quantize(2,2,0,0,1)
    if useList[2] == 4 : img = img.quantize(2,3,0,0,1)
    img = img.convert('1')
    if zFlip == 1 : img = ImageOps.flip(ImageOps.mirror(img))
    return img

# Hardware reset
def reset():
    digital_write(EPD_RST_PIN, 1)
    delay_ms(200) 
    digital_write(EPD_RST_PIN, 0)
    delay_ms(5)
    digital_write(EPD_RST_PIN, 1)
    delay_ms(200)   

def send_command(command):
    digital_write(EPD_DC_PIN, 0)
    digital_write(EPD_CS_PIN, 0)
    spi_writebyte([command])
    digital_write(EPD_CS_PIN, 1)

def send_data(data):
    digital_write(EPD_DC_PIN, 1)
    digital_write(EPD_CS_PIN, 0)
    spi_writebyte([data])
    digital_write(EPD_CS_PIN, 1)
    
def ReadBusy():
    while(digital_read(EPD_BUSY_PIN) == 1):      # 0: idle, 1: busy
        delay_ms(100)    

def TurnOnDisplay():
    send_command(0x22)
    send_data(0xC7)
    send_command(0x20)        
    ReadBusy()
    
def TurnOnDisplayPart():
    send_command(0x22)
    send_data(0x0c)
    send_command(0x20)        
    ReadBusy()
    
def init(update):
    if (module_init() != 0):
        return -1
    # EPD hardware init start
    reset()
    if(update == EPD_FULL_UPDATE):
        ReadBusy()
        send_command(0x12) # soft reset
        ReadBusy()
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
        send_data(EPD_LUT_FULL[70])
        send_command(0x04) #
        send_data(EPD_LUT_FULL[71])
        send_data(EPD_LUT_FULL[72])
        send_data(EPD_LUT_FULL[73])
        send_command(0x3A)     #Dummy Line
        send_data(EPD_LUT_FULL[74])
        send_command(0x3B)     #Gate time
        send_data(EPD_LUT_FULL[75])
        send_command(0x32)
        for count in range(70):
            send_data(EPD_LUT_FULL[count])
        send_command(0x4E)   # set RAM x address count to 0
        send_data(0x00)
        send_command(0x4F)   # set RAM y address count to 0X127
        send_data(0xF9)
        send_data(0x00)
        ReadBusy()
    else:
        send_command(0x2C)     #VCOM Voltage
        send_data(0x26)
        ReadBusy()
        send_command(0x32)
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
        ReadBusy()
        send_command(0x3C) #BorderWavefrom
        send_data(0x01)
    return 0

def getbuffer(image):
    if EPD_WIDTH%8 == 0:
        linewidth = int(EPD_WIDTH/8)
    else:
        linewidth = int(EPD_WIDTH/8) + 1
    buf = [0xFF] * (linewidth * EPD_HEIGHT)
    imwidth, imheight = image.size
    pixels = image.load()
    if(imwidth == EPD_WIDTH and imheight == EPD_HEIGHT):
        for y in range(imheight):
            for x in range(imwidth):                    
                if pixels[x, y] == 0:
                    x = imwidth - x
                    buf[int(x / 8) + y * linewidth] &= ~(0x80 >> (x % 8))
    elif(imwidth == EPD_HEIGHT and imheight == EPD_WIDTH):
        for y in range(imheight):
            for x in range(imwidth):
                newx = y
                newy = EPD_HEIGHT - x - 1
                if pixels[x, y] == 0:
                    newy = imwidth - newy - 1
                    buf[int(newx / 8) + newy*linewidth] &= ~(0x80 >> (y % 8))
    return buf

# width: 122
# height: 250 (32 if buffer)
# buffer changes height
# height in the code is really width

def bufferXO():
    buffer = ([0x00] + ([0xFF] * 3903))
    return buffer

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
    
def display(image):
    if EPD_WIDTH%8 == 0:
        linewidth = int(EPD_WIDTH/8)
    else:
        linewidth = int(EPD_WIDTH/8) + 1

    send_command(0x24)
    for j in range(0, EPD_HEIGHT):
        for i in range(0, linewidth):
            send_data(image[i + j * linewidth])   
    TurnOnDisplay()

def displayIgnoreOther(image):
    send_command(0x24)
    for j in range(0, 122):
        for i in range(0, 32):
            send_data(image[i + j * 32])   
    TurnOnDisplay()
    
def displayPartial(image):
    if EPD_WIDTH%8 == 0:
        linewidth = int(EPD_WIDTH/8)
    else:
        linewidth = int(EPD_WIDTH/8) + 1

    send_command(0x24)
    for j in range(0, EPD_HEIGHT):
        for i in range(0, linewidth):
            send_data(image[i + j * linewidth])   
            
            
    send_command(0x26)
    for j in range(0, EPD_HEIGHT):
        for i in range(0, linewidth):
            send_data(~image[i + j * linewidth])  
    TurnOnDisplayPart()

def displayPartBaseImage(image):
    if EPD_WIDTH%8 == 0:
        linewidth = int(EPD_WIDTH/8)
    else:
        linewidth = int(EPD_WIDTH/8) + 1

    send_command(0x24)
    for j in range(0, EPD_HEIGHT):
        for i in range(0, linewidth):
            send_data(image[i + j * linewidth])   
            
            
    send_command(0x26)
    for j in range(0, EPD_HEIGHT):
        for i in range(0, linewidth):
            send_data(image[i + j * linewidth])  
    TurnOnDisplay()

def Clear(color):
    if EPD_WIDTH%8 == 0:
        linewidth = int(EPD_WIDTH/8)
    else:
        linewidth = int(EPD_WIDTH/8) + 1
    
    send_command(0x24)
    for j in range(0, EPD_HEIGHT):
        for i in range(0, linewidth):
            send_data(color)
            
    # send_command(0x26)
    # for j in range(0, EPD_HEIGHT):
        # for i in range(0, linewidth):
            # send_data(color)   
            
    TurnOnDisplay()

def sleep():
    # send_command(0x22) #POWER OFF
    # send_data(0xC3)
    # send_command(0x20)

    send_command(0x10) #enter deep sleep
    send_data(0x03)
    delay_ms(2000)
    module_exit()




