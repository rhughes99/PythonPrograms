"""
Playing around with toggling P8_10 as fast as possible.

Requires Adafruit BBIO GPIO library.
Last modified: 08/16/2017
"""

import Adafruit_BBIO.GPIO as GPIO
import time

GPIO.setup("P8_10", GPIO.OUT)
GPIO.setup("P8_12", GPIO.IN)

# sleepTime = 0.0005
sleepTime = 5e-4

try:
    while True:
        print "Waiting..."
        GPIO.wait_for_edge("P8_12", GPIO.RISING)  # blocking
        time.sleep(0.5)                           # debounce
        
        print "Running..."
        count = 5 / sleepTime
        while count > 0:
            GPIO.output("P8_10", GPIO.HIGH)
            time.sleep(sleepTime)
            GPIO.output("P8_10", GPIO.LOW)
            time.sleep(sleepTime)
            count -= 1

except KeyboardInterrupt:
    print "Cleaning up and exiting."
    GPIO.cleanup()
    
