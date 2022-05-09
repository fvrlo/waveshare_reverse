import spidev
import RPi.GPIO
import os
from PIL import ImageFont
global GPIO
global SPI
GPIO = RPi.GPIO
SPI = spidev.SpiDev()

global EPD_image
global EPD_draw
EPD_image = 0
EPD_draw = 0


global pic_dir
maindir = os.path.abspath(os.path.join(os.path.dirname(os.path.realpath(__file__)), '..'))
pic_dir = maindir + '/pic'
pic_font15 = ImageFont.truetype(os.path.join(pic_dir, 'Font.ttc'), 15)
pic_font24 = ImageFont.truetype(os.path.join(pic_dir, 'Font.ttc'), 24)
pic_fontBIG = ImageFont.truetype(os.path.join(pic_dir, 'Font.ttc'), 122)




global EPD_WIDTH
global EPD_HEIGHT
global EPD_RST_PIN
global EPD_DC_PIN
global EPD_CS_PIN
global EPD_BUSY_PIN
global EPD_FULL_UPDATE
global EPD_PART_UPDATE
global EPD_LUT_FULL
global EPD_LUT_PART

lut_full = [
0x80,0x60,0x40,0x00,0x00,0x00,0x00,     #LUT0: BB:     VS 0 ~7
0x10,0x60,0x20,0x00,0x00,0x00,0x00,     #LUT1: BW:     VS 0 ~7
0x80,0x60,0x40,0x00,0x00,0x00,0x00,     #LUT2: WB:     VS 0 ~7
0x10,0x60,0x20,0x00,0x00,0x00,0x00,     #LUT3: WW:     VS 0 ~7
0x00,0x00,0x00,0x00,0x00,0x00,0x00,     #LUT4: VCOM:   VS 0 ~7
0x03,0x03,0x00,0x00,0x02,       # TP0 A~D RP0
0x09,0x09,0x00,0x00,0x02,       # TP1 A~D RP1
0x03,0x03,0x00,0x00,0x02,       # TP2 A~D RP2
0x00,0x00,0x00,0x00,0x00,       # TP3 A~D RP3
0x00,0x00,0x00,0x00,0x00,       # TP4 A~D RP4
0x00,0x00,0x00,0x00,0x00,       # TP5 A~D RP5
0x00,0x00,0x00,0x00,0x00,       # TP6 A~D RP6
0x15,0x41,0xA8,0x32,0x30,0x0A]

lut_part = [
0x00,0x00,0x00,0x00,0x00,0x00,0x00,
0x80,0x00,0x00,0x00,0x00,0x00,0x00,
0x40,0x00,0x00,0x00,0x00,0x00,0x00,
0x00,0x00,0x00,0x00,0x00,0x00,0x00,
0x00,0x00,0x00,0x00,0x00,0x00,0x00,
0x0A,0x00,0x00,0x00,0x00,
0x00,0x00,0x00,0x00,0x00,
0x00,0x00,0x00,0x00,0x00,
0x00,0x00,0x00,0x00,0x00,
0x00,0x00,0x00,0x00,0x00,
0x00,0x00,0x00,0x00,0x00,
0x00,0x00,0x00,0x00,0x00,
0x15,0x41,0xA8,0x32,0x30,0x0A]


#variables
EPD_WIDTH           = 122
EPD_HEIGHT          = 250
EPD_RST_PIN         = 17
EPD_DC_PIN          = 25
EPD_CS_PIN          = 8
EPD_BUSY_PIN        = 24
EPD_FULL_UPDATE     = 0
EPD_PART_UPDATE     = 1
EPD_LUT_FULL        = lut_full
EPD_LUT_PART        = lut_part