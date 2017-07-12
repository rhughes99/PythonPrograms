# i2cTemperatureSensorIF.py
# Collect temperature data from 1-wire sensors in basement
# 07/04/2017

import DS2482
import array
import time

# Sensor codes and locations
# Sensor 0 (0x5F000003AA865228) - breadboard, basement ambient temperature
# Sensor 1 (0xB1000003AA618A28) - main house radiator return temperature
# Sensor 2 (0xD5000003AA892E28) - library radiator return temperature
# Sensor 3 (0xFA000003AAABC228) - radiator supply temperature
# Sensor 4 (0x77000003AA72EB28) - H20 heater input temperature
# Sensor 5 (0x16000003AAAA6E28) - H20 heater output temperature
# Sensor 6 (0xBC0000043EFFC128) - Outside temperature
romCode = [[0x28,0x52,0x86,0xAA,0x03,0x00,0x00,0x5F], 
		   [0x28,0x8A,0x61,0xAA,0x03,0x00,0x00,0xB1], 
		   [0x28,0x2E,0x89,0xAA,0x03,0x00,0x00,0xD5], 
		   [0x28,0xC2,0xAB,0xAA,0x03,0x00,0x00,0xFA], 
		   [0x28,0x6E,0xAA,0xAA,0x03,0x00,0x00,0x16], 
		   [0x28,0xEB,0x72,0xAA,0x03,0x00,0x00,0x77], 
		   [0x28,0xC1,0xFF,0x3E,0x04,0x00,0x00,0xBC]]	

crcTable = [0, 94, 188, 226, 97, 63, 221, 131, 194, 156, 126, 32, 163, 253, 31, 65,
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

print "========================================"

#temperatureController = DS2482.DS2482(address=0x18, busnum=1)
#temperatureController = DS2482.DS2482()
temperatureController = DS2482.DS2482(address=0x18, busnum=2)

result = temperatureController.DS2482_reset()
if result:
	pass
else:
	print "*** DS2482_reset returned False"

# Select Active PullUp - required when >1 sensor connected to bus
temperatureController.DS2482_writeConfiguration(0x01)

#________________________________________________
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
timestr = time.ctime(time.time())
print "---------- Temperature conversion started: %s ----------" % (timestr)

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
for sensor in range(7):
	# All DS18B20 transactons start with initialization (reset OW bus)
	temperatureController.DS2482_owReset()
	
	# Send DS18B20 Match ROM command
	temperatureController.DS2482_owWriteByte(0x55)		# DS18B20 Match ROM
	
	# Send 8 bytes of ROM code
	for romByte in range(8):
		temperatureController.DS2482_owWriteByte(romCode[sensor][romByte])
#		print "romCode=%X" % (romCode[sensor][romByte])
	
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
#		scratchPad.insert(i, temperatureController._device.readRaw8())
		scratchPad.append(temperatureController._device.readRaw8())
		crc8 = crcTable[crc8 ^ scratchPad[i]]
	
	if crc8 == 0:
		# Convert scratchpad bytes 0 (LSB) & 1 (MSB) to temperature
		temperatureDegC = (scratchPad[0] / 16.0) + (scratchPad[1] & 0x07) * 16.0;
		if scratchPad[1] & 0x08:		# temperature <0 deg C
			temperatureDegC = temperatureDegC - 128.0
		
		temperatureDegF = 9.0 / 5.0 * temperatureDegC + 32.0
		
		if sensor == 0:
			print "Basement ambient temperature\t\t= %0.1f deg F" % (temperatureDegF)
		
		elif sensor == 1:
			print "Main house radiator return temperature\t= %0.1f deg F" % (temperatureDegF)
		
		elif sensor == 2:
			print "Library radiator return temperature\t= %0.1f deg F" % (temperatureDegF)
		
		elif sensor == 3:
			print "Radiator supply temperature\t\t= %0.1f deg F" % (temperatureDegF)
		
		elif sensor == 4:
			print "H20 heater input temperature\t\t= %0.1f deg F" % (temperatureDegF)
		
		elif sensor == 5:
			print "H20 heater output temperature\t\t= %0.1f deg F" % (temperatureDegF)
		
		elif sensor == 6:
			print "Outside temperature\t\t\t= %0.1f deg F" % (temperatureDegF)
		
		else:
			print "*** Need to add some code!!!"
	
	else:
		print "*** scratchPad data checksum BAD for sensor %d" % (sensor)
