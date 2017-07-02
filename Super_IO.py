# Super_IO.py
# Where we exercise a little of everything
# 04/14/2015

import Adafruit_BBIO.GPIO as GPIO
import Adafruit_BBIO.ADC as ADC

from Adafruit_LED_Backpack import Matrix8x8
from Adafruit_LED_Backpack import SevenSegment
import Image
import ImageDraw

import numpy as np
import time
import os
import sys

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
if ROOT_DIR not in sys.path:
    sys.path.append(ROOT_DIR)
import MCP4725


# Set up GPIO for LED blink
GPIO.setup("P8_10", GPIO.OUT)
ledOn = False

# Set up DAC parameters
dac = MCP4725.DAC()
#sig = lambda t: 50 * np.sin(t*5*2*np.pi) + 50

# Set up ADC parameters
ADC.setup()
adcInPin = 'P9_39'		# AIN0

# Create 7-segment display instance (default I2C address = 0x70)
sevenSegDisplay = SevenSegment.SevenSegment(address=0x70, busnum=1)
sevenSegDisplay.begin()
sevenSegDisplay.set_colon(False)
sevenSegDisplay.clear()

# Create matrix display instance
matrixDisplay = Matrix8x8.Matrix8x8(address=0x71, busnum=1)
matrixDisplay.begin()
matrixDisplay.clear()
matrixImage = False

#tZero = time.time()
lastTime = time.time()
dacValue = 0
while True:
	currentTime = time.time()
	deltaTime = currentTime - lastTime
	
	if deltaTime > 0.25:
		# DAC
#		dacValue = sig(currentTime-tZero)
		dacValue += 16
		if dacValue > 4095:
			dacValue = 0
		
#		dac.set_voltage(dacValue)
		dac.send_voltage(dacValue)
		dacVolts = dacValue / 4096.0 * 3.385
		
		# Toggle LED
		ledOn = not ledOn
		if ledOn:
			GPIO.output("P8_10", GPIO.HIGH)
		else:
			GPIO.output("P8_10", GPIO.LOW)
		
		# Matrix image
		image = Image.new('1', (8, 8))
		draw = ImageDraw.Draw(image)
		matrixImage = not matrixImage
		if matrixImage:
			draw.rectangle((0,0,7,7), outline=255, fill=0)
		else:
			draw.line((1,1,6,6), fill=255)
			draw.line((1,6,6,1), fill=255)

		matrixDisplay.set_image(image)
		matrixDisplay.write_display()		
		
		# Put dacValue on display
		sevenSegDisplay.clear()
		sevenSegDisplay.print_float(dacValue, decimal_digits=0)
		sevenSegDisplay.write_display()
		
		# ADC
		adcValue = ADC.read(adcInPin)
		adcVolts = adcValue * 1.800
#		print('dacValue= %d\tdacVolts= %f\tadcValue= %f\tadcVolts= %f\t2*adcVolts= %f' % (dacValue, dacVolts, adcValue, adcVolts, 2*adcVolts))
		print('dacVolts= %.3f\t2*adcVolts= %.3f\tdiff= %.3f' % (dacVolts, 2*adcVolts, dacVolts-2*adcVolts))
		
		lastTime = currentTime

