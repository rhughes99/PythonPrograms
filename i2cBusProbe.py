"""
Playing around with probing i2c bus, determining which devices are plugged in.

Last touched: 08/18/2017
"""

import time
import DS2482
#import MCP4725
from Adafruit_LED_Backpack import SevenSegment
from Adafruit_LED_Backpack import Matrix8x8
from PIL import Image
from PIL import ImageDraw

# Try known I2C interfaces, looking for exceptions

oneWireNetwork = 1
try:
	temperatureController = DS2482.DS2482(address=0x18, busnum=2)
	result = temperatureController.DS2482_reset()
#except IOError as e:
except Exception:
	oneWireNetwork = 0
	print "*** Temperature network not found"


#dacModule = 1
#try:
#	dac = MCP4725.DAC()
#except IOError as e:
dacModule = 0
#	print "*** MCP4725 DAC not found"


sevenSegDisplay = 1
try:
	sevenDisplay = SevenSegment.SevenSegment(address=0x70, busnum=2)
	sevenDisplay.begin()
	sevenDisplay.clear()
#except IOError as e:
except Exception:
	sevenSegDisplay = 0
	print "*** Seven segment module not found"


matrixDisplay = 1
try:
	matDisplay = Matrix8x8.Matrix8x8(address=0x71, busnum=2)
	matDisplay.begin()
	matDisplay.clear()
except IOError as e:
#except Exception:
	matrixDisplay = 0
	print "*** 8x8 matrix module not found"


if oneWireNetwork == 1:
	print "Temperature network on-line"

if dacModule == 1:
	print "MCP4725 DAC on-line"

if sevenSegDisplay == 1:
	print "Seven segment module on-line"

if matrixDisplay == 1:
	print "8x8 matrix display on-line"

print "---- End of bus scan ----"
time.sleep(1)


colon = False
if sevenSegDisplay == 1:
	for i in range(0xFF):
		sevenDisplay.clear()
		sevenDisplay.print_hex(i)
		sevenDisplay.set_colon(colon)
		sevenDisplay.write_display()
		time.sleep(0.05)
	
	sevenDisplay.print_hex(0xAA)


if matrixDisplay == 1:
	matDisplay.clear()
	
	# First create an 8x8 1 bit color image
	image = Image.new('1', (8, 8))
	
	# Then create a draw instance
	draw = ImageDraw.Draw(image)
	
	# Draw a rectangle with colored outline
	draw.rectangle((0,0,7,7), outline=255, fill=0)
	
	# Draw an X with two lines
	draw.line((1,1,6,6), fill=255)
	draw.line((1,6,6,1), fill=255)
	
	# Draw image on display buffer
	matDisplay.set_image(image)
	
	# Draw buffer to display hardware
	matDisplay.write_display()



print "---- The End ----"
