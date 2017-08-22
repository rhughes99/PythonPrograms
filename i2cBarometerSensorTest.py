"""
Test of MPL3116A2 barometer sensor.

Last touched: 08/22/2017
"""

import MPL3116A2_Barometer as baroSense
import time

print "========================================"

baroController = baroSense.Barometer(address=0x60, busnum=2)

status, ctrl1, ctrl2, ctrl3, ctrl4, ctrl5 = baroController.getStatusAndControlRegisters()
print "Status:"
print "0x%X 0x%X 0x%X 0x%X 0x%X 0x%X " % (status, ctrl1, ctrl2, ctrl3, ctrl4, ctrl5)

if status & 0x80:
	print "\t*** PTOW = Pressure/Altitude or Temperature data overwrite"

if status & 0x40:
	print "\t*** Pressure/Altitude data overwrite"

if status & 0x20:
	print "\t*** Temperature data overwrite"

if status & 0x08:
	print "\tPressure/Altitude or Tempeerature new data ready"

if status & 0x04:
	print "\tPressure/Altitude new data ready"

if status & 0x02:
	print "\tTemperature new data ready"


baroController.setPressureEventFlag()

baroController.setBarometerMode()
#baroController.setAltimeterMode()

T_ZERO = time.time()
while 1:
	avgPressure    = 0
	avgPressDelta  = 0
	avgAltitude    = 0
	avgAltDelta    = 0
	avgTemperature = 0
	avgTempDelta   = 0
	
	startTime = time.time()
	for n in range(10):		
		currentPressure   = baroController.getPressure()
		currentPressDelta = baroController.getPressureDelta()
		avgPressure   += currentPressure
		avgPressDelta += currentPressDelta
		
#		currentAlt      = baroController.getAltitude()
#		currentAltDelta = baroController.getAltitudeDelta()
#		avgAltitude += currentAlt
#		avgAltDelta += currentAltDelta
		
		currentTemp      = baroController.getTemperature()
		currentTempDelta = baroController.getTemperatureDelta()
		avgTemperature += currentTemp
		avgTempDelta   += currentTempDelta
		
		time.sleep(0.7)
	
	timeTag = (startTime + (time.time() - startTime) / 2) - T_ZERO
	
	avgPressure    /= 10
	avgPressDelta  /= 10
	avgAltitude    /= 10
	avgAltDelta    /= 10
	avgTemperature /= 10
	avgTempDelta   /= 10
	
#	print "avgPressure    = %.2f inch Hg" % (avgPressure)
#	print "avgAltitude    = %.1f ft" % (avgAltitude)
#	print "avgTemperature = %.1f deg F\n" % (avgTemperature)
#	print "%d\t%f\t%f\t%f\t%f\t%f\t%f" % (timeTag, avgPressure, avgPressDelta, avgAltitude, avgAltDelta, avgTemperature, avgTempDelta)
	print "%d\t%f\t%f" % (timeTag, avgPressure, avgTemperature)
