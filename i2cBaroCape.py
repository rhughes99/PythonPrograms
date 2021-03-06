"""
Collects temperature and barometric data using BaroCape.

Writes data to BaroData.txt.
Last touched: 01/17/2019
"""

import array
import sys
import time
import datetime
import DS2482
from Adafruit_LED_Backpack import SevenSegment
import MPL3116A2_Barometer as BaroSense

SAMPLE_PERIOD = 30		# seconds between data samples

# Temperature sensor codes and locations
# Sensor 0 (0x5F000003AA865228) - breadboard, basement ambient temperature
# Sensor 1 (0xB1000003AA618A28) - main house radiator return temperature
# Sensor 2 (0xD5000003AA892E28) - library radiator return temperature
# Sensor 3 (0xFA000003AAABC228) - radiator supply temperature
# Sensor 4 (0x77000003AA72EB28) - H20 heater input temperature
# Sensor 5 (0x16000003AAAA6E28) - H20 heater output temperature
# Sensor 6 (0xBC0000043EFFC128) - Outside temperature
ROM_CODE = [[0x28,0x52,0x86,0xAA,0x03,0x00,0x00,0x5F],
			[0x28,0x8A,0x61,0xAA,0x03,0x00,0x00,0xB1],
			[0x28,0x2E,0x89,0xAA,0x03,0x00,0x00,0xD5],
			[0x28,0xC2,0xAB,0xAA,0x03,0x00,0x00,0xFA],
			[0x28,0x6E,0xAA,0xAA,0x03,0x00,0x00,0x16],
			[0x28,0xEB,0x72,0xAA,0x03,0x00,0x00,0x77],
			[0x28,0xC1,0xFF,0x3E,0x04,0x00,0x00,0xBC]]

CRC_TABLE = [0, 94, 188, 226, 97, 63, 221, 131, 194, 156, 126, 32, 163, 253, 31, 65,
			 157, 195, 33, 127, 252, 162, 64, 30, 95, 1, 227, 189, 62, 96, 130, 220,
			 35, 125, 159, 193, 66, 28, 254, 160, 225, 191, 93, 3, 128, 222, 60, 98,
			 190, 224, 2, 92, 223, 129, 99, 61, 124, 34, 192, 158, 29, 67, 161, 255,
			 70, 24, 250, 164, 39, 121, 155, 197, 132, 218, 56, 102, 229, 187, 89, 7,
			 219, 133, 103, 57, 186, 228, 6, 88, 25, 71, 165, 251, 120, 38, 196, 154,
			 101, 59, 217, 135, 4, 90, 184, 230, 167, 249, 27, 69, 198, 152, 122, 36,
			 248, 166, 68, 26, 153, 199, 37, 123, 58, 100, 134, 216, 91, 5, 231, 185,
			 140, 210, 48, 110, 237, 179, 81, 15, 78, 16, 242, 172, 47, 113, 147, 205,
			 17, 79, 173, 243, 112, 46, 204, 146, 211, 141, 111, 49, 178, 236, 14, 80,
			 175, 241, 19, 77, 206, 144, 114, 44, 109, 51, 209, 143, 12, 82, 176, 238,
			 50, 108, 142, 208, 83, 13, 239, 177, 240, 174, 76, 18, 145, 207, 45, 115,
			 202, 148, 118, 40, 171, 245, 23, 73, 8, 86, 180, 234, 105, 55, 213, 139,
			 87, 9, 235, 181, 54, 104, 138, 212, 149, 203, 41, 119, 244, 170, 72, 22,
			 233, 183, 85, 11, 136, 214, 52, 106, 43, 117, 151, 201, 74, 20, 246, 168,
			 116, 42, 200, 150, 21, 75, 169, 247, 182, 232, 10, 84, 215, 137, 107, 53]

# First make sure required I2C devices are connected
# We need 1-wire interface to temperature sensors, MPL3116A barometer module,
#  and 7-segment display
try:
	temperatureController = DS2482.DS2482(address=0x18, busnum=2)
	result = temperatureController.DS2482_reset()
	if result:
		pass
	else:
		print "*** DS2482_reset returned False!"
		sys.exit()
except Exception:
	print "*** Temperature network not found!"
	sys.exit()

try:
	sevenSegDisplay = SevenSegment.SevenSegment(address=0x70, busnum=2)
	sevenSegDisplay.begin()
	sevenSegDisplay.clear()
except Exception:
	print "*** Seven segment module not found!"
	sys.exit()

try:
	baroController = BaroSense.Barometer(address=0x60, busnum=2)
	status, ctrl1, ctrl2, ctrl3, ctrl4, ctrl5 = \
		baroController.getStatusAndControlRegisters()
except Exception:
	print "*** MPL3116A2 barometer module not found!"
	sys.exit()


#________________________________________________
def main():
	# Required devices present; initialize them

	# Temperature sensor network
	# Select Active PullUp - required when >1 sensor connected to bus
	temperatureController.DS2482_writeConfiguration(0x01)

	# Barometer module
	baroController.setPressureEventFlag()
	baroController.setBarometerMode()

	# Display - display current time
#	now = datetime.datetime.now()
#	hour = now.hour - 5       			# convert to local time
#	minute = now.minute
#	second = now.second

	sevenSegDisplay.clear()
	# Set hours
#	sevenSegDisplay.set_digit(0, int(hour / 10))	# Tens
#	sevenSegDisplay.set_digit(1, hour % 10)			# Ones
	# Set minutes
#	sevenSegDisplay.set_digit(2, int(minute / 10))	# Tens
#	sevenSegDisplay.set_digit(3, minute % 10)		# Ones
	# Toggle colon
#	sevenSegDisplay.set_colon(1)

#	SetSevenSegDisplay(int(hour/10), hour%10, int(minute/10), minute%10)

	numSamples = 0

	# Open data file
	file = open("BaroData.txt",'w')
	file.write("Date\tTime\tOut Temp\tIn Temp\tPressure\tMain Rad Temp\tLib Rad Temp\tRad Supply Temp\tH2O In Temp\tH2O Out Temp\n")
	file.close()

	# Ready to go - pause to catch our breath
	print "\n=============================="
	time.sleep(1.0)

	sevenSegDisplay.set_colon(False)
	print ("[Date\t\tTime]\t[Out-Temp  In-Temp  Press]\t[Main-Rad  Lib-Rad  Rad-Supply]\t\
		[H2O-In  H2O-Out]")

	while True:
		try:
			now = time.localtime()
			today = datetime.date.today()
#			print "%s\t%d:%d:%d" % (today, now[3], now[4], now[5])

			# Turn 7-seg colon off to indicate measurements in progress
			sevenSegDisplay.set_colon(False)
			
			ambTempF,mainRadTempF,libRadTempF,radSupTempF,h2oInTempF,h2oOutTempF,outTempF = \
				GetTemperatureData()
			currentPressure,currentPressDelta = GetBarometerData()
			numSamples += 1

			# Print what we are putting in BaroData.txt
			print ("[%s  %d:%d:%d]\t[%.1f\t%.1f\t%.1f]\t\t[%.1f\t%.1f\t%.1f]\t\t[%.1f\t%.1f]" % 
				(today, now[3]-5, now[4], now[5], outTempF, ambTempF, currentPressure, 
				mainRadTempF, libRadTempF, radSupTempF, h2oInTempF, h2oOutTempF))

			file = open("BaroData.txt",'a')
			file.write("%s\t%d:%d:%d\t%.1f\t%.1f\t%.2f\t%.2f\t%.2f\t%.2f\t%.2f\t%.2f\n" %
				(today, now[3]-5, now[4], now[5], outTempF, ambTempF, currentPressure,
				mainRadTempF, libRadTempF, radSupTempF, h2oInTempF, h2oOutTempF))
			file.close()

			# Display pressure on 7-seg display
#			sevenSegDisplay.print_float(currentPressure)
#			sevenSegDisplay.write_display()

			# Display time on 7-seg display
			DisplayCurrentTime()	# also turns colon back on

			time.sleep(SAMPLE_PERIOD)
		except KeyboardInterrupt:
			print " -----------------------------"
			print "%d samples" % (numSamples)
			sys.exit()


#________________________________________________
def GetTemperatureData():
	# Initiate temperature conversion for all sensors
	# 	Send 1-Wire Reset
	# 	Send Skip ROM command (address all 1-Wire devices)
	# 	Send Convert T command
	# 	Start temperature conversion timer

	# All DS18B20 transactons start with initialization (reset OW bus)
	temperatureController.DS2482_owReset()

	# Send DS18B20 Skip ROM command
	temperatureController.DS2482_owWriteByte(0xCC)		# DS18B20 Skip ROM

	# Send DS18B20 Convert T command
	temperatureController.DS2482_owWriteByte(0x44)		# DS18B20 Convert T

	# Capture and display conversion time
#	timestr = time.ctime(time.time())
#	print "----- [%d] Temperature conversion started: %s -----" % (numTempSamples+1,timestr)

	# Wait for temperature conversion (750 ms for 12 bits)
	time.sleep(0.8)

	# Individually read temperature from each connected sensor
	# 	Send 1-Wire Reset
	# 	Send Match ROM command
	# 	Send Read Scratchpad command
	# 	Repeat 9 times
	# 	Repeat 8 times
	# 	Send 1-Wire Read Byte command
	# 	Set DS2482 read pointer to Data Register
	# 	Read byte from DS2482
	# 	Convert data to temperature

	ambTempF		= -999
	mainRadTempF	= -999
	libRadTempF		= -999
	radSupTempF		= -999
	h2oInTempF		= -999
	h2oOutTempF		= -999
	outTempF		= -999
	for sensor in range(7):
		# All DS18B20 transactons start with initialization (reset OW bus)
		temperatureController.DS2482_owReset()

		# Send DS18B20 Match ROM command
		temperatureController.DS2482_owWriteByte(0x55)		# DS18B20 Match ROM

		# Send 8 bytes of ROM code
		for romByte in range(8):
			temperatureController.DS2482_owWriteByte(ROM_CODE[sensor][romByte])

		# Send DS18B20 Read Scratchpad command
		temperatureController.DS2482_owWriteByte(0xBE)		# DS18B20 Read Scratchpad

		crc8 = 0
		scratchPad = array.array('B',[])
		# Read 9 bytes of scratchpad
		for i in range(9):
			temperatureController.DS2482_owReadByte()

			# Set read pointer
			temperatureController.DS2482_setReadPointer(DS2482.DS2482_READ_DATA_REG)

			# Read byte from DS2482
			scratchPad.append(temperatureController._device.readRaw8())
			crc8 = CRC_TABLE[crc8 ^ scratchPad[i]]

		if crc8 == 0:
			# Convert scratchpad bytes 0 (LSB) & 1 (MSB) to temperature
			temperatureDegC = (scratchPad[0] / 16.0) + (scratchPad[1] & 0x07) * 16.0;
			if scratchPad[1] & 0x08:		# temperature <0 deg C
				temperatureDegC = temperatureDegC - 128.0

			temperatureDegF = 9.0 / 5.0 * temperatureDegC + 32.0
			if sensor == 0:
				ambTempF = temperatureDegF

			elif sensor == 1:
				mainRadTempF = temperatureDegF

			elif sensor == 2:
				libRadTempF = temperatureDegF

			elif sensor == 3:
				radSupTempF = temperatureDegF

			elif sensor == 4:
				h2oInTempF = temperatureDegF

			elif sensor == 5:
				h2oOutTempF = temperatureDegF

			elif sensor == 6:
				outTempF = temperatureDegF

			else:
				print "*** Need to add some code!!!"

		else:
			print "*** scratchPad data checksum BAD for sensor %d" % (sensor)

#	print "Basement ambient\t\t= %0.1f deg F" % (ambTempF)
#	print "Outside\t\t\t\t= %0.1f deg F" % (outTempF)
#	print "Radiator supply\t\t\t= %0.1f deg F" % (radSupTempF)
#	print " Main house radiator return\t= %0.1f deg F" % (mainRadTempF)
#	print " Library radiator return\t= %0.1f deg F" % (libRadTempF)
#	print "H20 heater input\t\t= %0.1f deg F" % (h2oInTempF)
#	print "H20 heater output\t\t= %0.1f deg F" % (h2oOutTempF)

	return (ambTempF,mainRadTempF,libRadTempF,radSupTempF,h2oInTempF,h2oOutTempF,outTempF)

#________________________________________________
def GetBarometerData():
	# Returns current and delta barometric pressures in inch mercury

	currentPressure   = baroController.getPressure()
	currentPressDelta = baroController.getPressureDelta()
	return (currentPressure,currentPressDelta)

#________________________________________________
def SetSevenSegDisplay(a,b,c,d):
	sevenSegDisplay.set_digit(0, a)
	sevenSegDisplay.set_digit(1, b)
	sevenSegDisplay.set_digit(2, c)
	sevenSegDisplay.set_digit(3, d)
	sevenSegDisplay.set_colon(True)

	# Write display buffer to hardware
	# Must be called to update actual display LEDs
	sevenSegDisplay.write_display()

#________________________________________________
def DisplayCurrentTime():
	now = datetime.datetime.now()
	hour = now.hour - 5       			# convert to local time
	minute = now.minute
#	second = now.second
	SetSevenSegDisplay(int(hour/10), hour%10, int(minute/10), minute%10)

#________________________________________________
if __name__ == '__main__':
	main()
