# Routines for accessing DS2482-100 and connected 1-wire devices
# 09/08/2015

# --- Constants ---
DEFAULT_ADDRESS		= 0x18		# 00110<AD1><AD0>

# DS2482-100 Valid Pointer Codes
DS2482_STATUS_REG    = 0xF0
DS2482_READ_DATA_REG = 0xE1
DS2482_CONFIG_REG    = 0xC3

# DS2482-100 Status Register Bit Assignments
DS2482_STATUS_1WB	= 0x01;		# 1-Wire Busy
DS2482_STATUS_PPD	= 0x02;		# Presence-Pulse Detect
DS2482_STATUS_SD	= 0x04;		# Short Detected
DS2482_STATUS_LL 	= 0x08;		# Logic Level
DS2482_STATUS_RST	= 0x10;		# Device Reset
DS2482_STATUS_SBR	= 0x20;		# Single Bit Result
DS2482_STATUS_TSB	= 0x40;		# Triplet Second Bit
DS2482_STATUS_DIR	= 0x80;		# Branch Direction Taken

class DS2482(object):
	"""Driver for interfacing with Maxim DS2482-100 Single-Channel 1-Wire Master."""

	#________________________________________________
	def __init__(self, address=DEFAULT_ADDRESS, i2c=None, **kwargs):
		"""Create DS2482 driver for device on specified I2C address
		(defaults to 0x18) and I2C bus (defaults to platform specific bus).
		"""
		if i2c is None:
			import Adafruit_GPIO.I2C as I2C
			i2c = I2C
		self._device = i2c.get_i2c_device(address, **kwargs)

	#________________________________________________
	def DS2482_reset(self):
		"""Perform device reset on DS2482"""
		# Performs global reset of device state machine; terminates any ongoing 1-Wire communication
		# Restriction: None
		# Read Pointer Position: Status Register
		# Status Bits Affected: RST = 1; 1WB = PPD = SD = SBR = TSB = DIR = 0
		# Configuration Bits Affected: 1WS = APU = SPU = 0
		# Returns True if device reset, False if problem or no device
		self._device.writeRaw8(0xF0)
		response = self._device.readRaw8()
		if (response & DS2482_STATUS_RST) == DS2482_STATUS_RST:
			return True
		else:
			print "*** Exiting DS2482_reset FAIL"
			return False

	#________________________________________________
	def DS2482_setReadPointer(self,ptrCode):
		# Sets read pointer to specified register
		# Restriction: None
		# Read Pointer Position: As specified by ptrCode
		# Status Bits Affected: None
		# Configuration Bits Affected: None
		# Returns True
		self._device.write8(0xE1,ptrCode)
		return True
	
	#________________________________________________
	def DS2482_writeConfiguration(self,config):
		# Writes new configuration, settings take effect immediately
		# Restriction: 1-Wire activity must have ended (1WB = 0)
		# Read Pointer Position: Configuration Register
		# Status Bits Affected: RST = 0
		# Configuration Bits Affected: 1WS, SPU & APU updated
		# Returns True if success, False if problem
		self._device.write8(0xD2,(config | (~config<<4)))
		response = self._device.readRaw8()
		if response == config:
			return True
		else:
			print "*** Exiting DS2482_writeConfiguration FAIL"
			return False
	
	#________________________________________________
	def DS2482_owReset(self):
		# Generates 1-Wire reset/presence-detect cycle
		# Restriction: 1-Wire activity must have ended (1WB = 0)
		# Read Pointer Position: Status Register
		# Status Bits Affected: 1WB, PPD, SD
		# Configuration Bits Affected: 1WS, APU, SPU
		# Returns True if no issue, False if problem or no device
		stillWaiting = True
		self.waitForOWBusAvailable()
		self._device.writeRaw8(0xB4)
		
		# Loop while checking 1WB for completion of 1-Wire operation
		# Don't use waitForOWBusAvailable here because we want to
		#  check several status bits after waiting
		while stillWaiting:
			response = self._device.readRaw8()
			if response & DS2482_STATUS_1WB:		# 1WBusy = 1 if busy
				pass
			else:
				stillWaiting = False
		
		# Check for short condition
		if response & DS2482_STATUS_SD:
			print "  *** 1-Wire short detected"
		
		# Check for presence detect
#		if response & DS2482_STATUS_PPD:
#			print "  1-Wire presence pulse detected"
		
		return True
	
	#________________________________________________
	def DS2482_owWriteByte(self,data):
		# Writes single byte to 1-Wire line
		# Restriction: 1-Wire activity must have ended (1WB = 0)
		# Read Pointer Position: Status Register
		# Status Bits Affected: 1WB (set to 1 for 8 x tSLOT)
		# Configuration Bits Affected: 1WS, APU, SPU
		# Returns True
	 	self.waitForOWBusAvailable()
		self._device.write8(0xA5,data)
		return True
	
	#________________________________________________
	def DS2482_owReadByte(self):
		# Generates eight read-data time slots on 1-Wire line
		# Restriction: 1-Wire activity must have ended (1WB = 0)
		# Read Pointer Position: Status Register
		# Note: To read data byte received from 1-Wire line, issue
		# Set Read Pointer command and select the Read Data Register.
		# Then access DS2482-100 in read mode.
		# Status Bits Affected: 1WB (set to 1 for 8 x tSLOT)
		# Configuration Bits Affected: 1WS, APU
		# Returns True
		self.waitForOWBusAvailable()
		self._device.writeRaw8(0x96)
		return True
	
	#________________________________________________
	def waitForOWBusAvailable(self):
		# Reads DS2482 Status Register and returns when 1-Wire bus is not busy
		# or if cycle count exceeds threshold
		stillWaiting = True
		cycles = 0
		
		self.DS2482_setReadPointer(DS2482_STATUS_REG)
		while stillWaiting:
			response = self._device.readRaw8()
			if response & DS2482_STATUS_1WB:
				pass
			else:
				stillWaiting = False
				
			cycles += 1
			if cycles > 10:
				print "*** Exceeded 10 cycles in waitForOWBusAvailable"
				return
