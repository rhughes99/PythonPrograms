"""
Playing with stepper motor control.

Requires Adafruit BBIO GPIO library.
Last touched: 08/18/2017
"""

import Adafruit_BBIO.GPIO as GPIO
import time

# Some constants
#ENABLE_PIN  = "P8_7"
COIL_A1_PIN = "P8_8"			# A1N1
COIL_A2_PIN = "P8_9"			# A1N2
COIL_B1_PIN = "P8_10"			# B1N1
COIL_B2_PIN = "P8_11"			# B1N2

# Set and initialize outputs
#GPIO.setup(ENABLE_PIN,  GPIO.OUT)
GPIO.setup(COIL_A1_PIN, GPIO.OUT)
GPIO.setup(COIL_A2_PIN, GPIO.OUT)
GPIO.setup(COIL_B1_PIN, GPIO.OUT)
GPIO.setup(COIL_B2_PIN, GPIO.OUT)

#GPIO.output(ENABLE_PIN,  1)				# 1 = motor controller module enabled
GPIO.output(COIL_A1_PIN, 0)
GPIO.output(COIL_A2_PIN, 0)
GPIO.output(COIL_B1_PIN, 0)
GPIO.output(COIL_B2_PIN, 0)

def Forward(delay, steps):  
	for i in range(0, steps):
		SetStep(1, 0, 1, 0)
		time.sleep(delay)
		SetStep(0, 1, 1, 0)
		time.sleep(delay)
		SetStep(0, 1, 0, 1)
		time.sleep(delay)
		SetStep(1, 0, 0, 1)
		time.sleep(delay)

def Backwards(delay, steps):  
  for i in range(0, steps):
		SetStep(1, 0, 0, 1)
		time.sleep(delay)
		SetStep(0, 1, 0, 1)
		time.sleep(delay)
		SetStep(0, 1, 1, 0)
		time.sleep(delay)
		SetStep(1, 0, 1, 0)
		time.sleep(delay)

def SetStep(w1, w2, w3, w4):
	GPIO.output(COIL_A1_PIN, w1)
	GPIO.output(COIL_A2_PIN, w2)
	GPIO.output(COIL_B1_PIN, w3)
	GPIO.output(COIL_B2_PIN, w4)

while True:
	delay = raw_input("Delay between steps (milliseconds) [5]:")
	steps = raw_input("How many steps forward [128]: ")
	Forward(int(delay) / 1000.0, int(steps))
	time.sleep(1)
	
#	steps = raw_input("How many steps backwards [128]: ")
	Backwards(int(delay) / 1000.0, int(steps))
