"""
Class for MPL3115A2 barometric sensor.

Refer to MPL3115A2 Altimeter.pdf and AN4519 Altimeter App Note.pdf.
Last touched: 08/24/2018
"""

import time

# --- Constants ---
MPL3115A2_DEFAULT_ADDRESS		= 0x60

# MPL3115A2 Registers 
MPL3115A2_REGISTER_STATUS		= 0x00			# alias for DR_STATUS or F_STATUS
#MPL3115A2_REGISTER_STATUS_TDR	= 0x02			#  Temperature new data available
MPL3115A2_REGISTER_STATUS_PDR	= 0x04			#  Pressure/Altitude new data available
#MPL3115A2_REGISTER_STATUS_PTDR	= 0x08			#  Pressure/Altitude OR Temperature data ready

MPL3115A2_REGISTER_PRESSURE_MSB	= 0x01			# OUT_P_MSB, bits 12-19 of 20-bit real-time Pressure sample
MPL3115A2_REGISTER_PRESSURE_CSB	= 0x02			# OUT_P_CSB, bits 4-11 of 20-bit real-time Pressure sample
MPL3115A2_REGISTER_PRESSURE_LSB	= 0x03			# OUT_P_LSB, bits 0-3 of 20-bit real-time Pressure sample

MPL3115A2_REGISTER_TEMP_MSB		= 0x04			# OUT_T_MSB, bits 4-11 of 12-bit real-time Temperature sample
MPL3115A2_REGISTER_TEMP_LSB		= 0x05			# OUT_T_LSB, bits 0-3 of 12-bit real-time Temperature sample

#MPL3115A2_REGISTER_DR_STATUS	= 0x06			# DR_STATUS, Data Ready status information

MPL3115A2_OUT_P_DELTA_MSB		= 0x07			# OUT_P_DELTA MSB, bits 12-19 of 20-bit Pressure change data
MPL3115A2_OUT_P_DELTA_CSB		= 0x08			# OUT_P_DELTA_CSB, bits 4-11 of 20-bit Pressure change data
MPL3115A2_OUT_P_DELTA_LSB		= 0x09			# OUT_P_DELTA_LSB, bits 0-3 of 20-bit Pressure change data

MPL3115A2_OUT_T_DELTA_MSB		= 0x0A			# OUT_T_DELTA_MSB, bits 4-11 of 12-bit Temperature change data
MPL3115A2_OUT_T_DELTA_LSB		= 0x0B			# OUT_T_DELTA_LSB, bits 0-3 of 12-bit Temperature change data

MPL3115A2_WHOAMI				= 0x0C			# 0xC4, Fixed Device ID Number

MPL3115A2_PT_DATA_CFG			= 0x13			# PT_DATA_CFG, data event flag configuration
#MPL3115A2_PT_DATA_CFG_TDEFE		= 0x01		#  Data event flag enable on new Temperature data
MPL3115A2_PT_DATA_CFG_PDEFE		= 0x02			#  Data event flag enable on new Pressure/Altitude data
#MPL3115A2_PT_DATA_CFG_DREM		= 0x04			#  Data ready event mode

MPL3115A2_CTRL_REG1				= 0x26			# CTRL_REG1, Modes, Oversampling
MPL3115A2_CTRL_REG1_SBYB		= 0x01			#  This bit is sets the mode to ACTIVE
#MPL3115A2_CTRL_REG1_OST			= 0x02		#  OST bit initiates a measurement immediately
#MPL3115A2_CTRL_REG1_RST			= 0x04		#  Software Reset
#MPL3115A2_CTRL_REG1_OS1			= 0x00		#  Oversample Ratio 000
#MPL3115A2_CTRL_REG1_OS2			= 0x08		#  Oversample Ratio 001
#MPL3115A2_CTRL_REG1_OS4			= 0x10		#  Oversample Ratio 010
#MPL3115A2_CTRL_REG1_OS8			= 0x18		#  Oversample Ratio 011
#MPL3115A2_CTRL_REG1_OS16		= 0x20			#  Oversample Ratio 100
#MPL3115A2_CTRL_REG1_OS32		= 0x28			#  Oversample Ratio 101
#MPL3115A2_CTRL_REG1_OS64		= 0x30			#  Oversample Ratio 110
#MPL3115A2_CTRL_REG1_OS128		= 0x38			#  Oversample Ratio 111
#MPL3115A2_CTRL_REG1_RAW			= 0x40		#  RAW output mode
MPL3115A2_CTRL_REG1_ALT			= 0x80			#  OR = Altimeter mode
MPL3115A2_CTRL_REG1_ALT_BAR		= 0x7F			#  AND = Barometer mode

MPL3115A2_CTRL_REG2				= 0x27			# CTRL_REG2, Acquisition time step
MPL3115A2_CTRL_REG3				= 0x28			# CTRL_REG3, Interrupt pin configuration
MPL3115A2_CTRL_REG4				= 0x29			# CTRL_REG4, Interrupt enables
MPL3115A2_CTRL_REG5				= 0x2A			# CTRL_REG5, Interrupt output pin assignment

#MPL3115A2_REGISTER_STARTCONVERSION	= 0x12		# ???

class Barometer(object):
	"""Driver for interfacing with Xtrinsic MPL3115A2 I2C Precision Altimeter."""
	
	ctrlReg1Data = 0
	ctrlReg2Data = 0
	
	#________________________________________________
	def __init__(self, address=MPL3115A2_DEFAULT_ADDRESS, i2c=None, **kwargs):
		"""Set I2C address to MPL3115A2 default"""
		
		if i2c is None:
			import Adafruit_GPIO.I2C as I2C
			i2c = I2C
		self._device = i2c.get_i2c_device(address, **kwargs)
		
		whoami = self._device.readU8(MPL3115A2_WHOAMI)
		if whoami != 0xC4:
			print "*** whoami = 0x%X (expected 0xC4)" (whoami)

	#________________________________________________
	def getStatusAndControlRegisters(self):
		"""Get Status and Control register values"""
		
		status   = self._device.readU8(MPL3115A2_REGISTER_STATUS)
		control1 = self._device.readU8(MPL3115A2_CTRL_REG1)
		control2 = self._device.readU8(MPL3115A2_CTRL_REG2)
		control3 = self._device.readU8(MPL3115A2_CTRL_REG3)
		control4 = self._device.readU8(MPL3115A2_CTRL_REG4)
		control5 = self._device.readU8(MPL3115A2_CTRL_REG5)
		return (status, control1, control2, control3, control4, control5)

	#________________________________________________
	def setStandbyMode(self):
		"""Put MPL3115A2 into Standby mode SBYB; all register writes must be done in Standby mode"""
		
		# Clear SBYB mask while holding all other values of CTRL_REG_1
		Barometer.ctrlReg1Data = self._device.readU8(MPL3115A2_CTRL_REG1)
		self._device.write8(MPL3115A2_CTRL_REG1, Barometer.ctrlReg1Data & ~MPL3115A2_CTRL_REG1_SBYB)

	#________________________________________________
	def setAltimeterMode(self):
		"""Put MPL3115A2 into Active Altimeter mode"""
		
		self.setStandbyMode()
		
		# Write 1 to ALT and SBYB bits to go into Active Altimeter mode
		self._device.write8(MPL3115A2_CTRL_REG1, (Barometer.ctrlReg1Data | MPL3115A2_CTRL_REG1_ALT | MPL3115A2_CTRL_REG1_SBYB))

	#________________________________________________
	def setBarometerMode(self):
		"""Put MPL3115A2 into Active Barometer mode"""
		
		self.setStandbyMode()
		
		# Write 0 to ALT and 1 to SBYB bits to go into Active Barometer mode
		self._device.write8(MPL3115A2_CTRL_REG1, (Barometer.ctrlReg1Data & MPL3115A2_CTRL_REG1_ALT_BAR | MPL3115A2_CTRL_REG1_SBYB))

	#________________________________________________
	def setOutputSampleRate(self, osr):
		"""Set OSR in CTRL_REG1"""
		
		self.setStandbyMode()
		
		# The OSR_Value is set to 0-7, corresponding to Ratios 1-128
		if osr < 8:
			osr = osr << 3
			Barometer.ctrlReg1Data = Barometer.ctrlReg1Data & 0xC7		# clear OS[2:0]
			self._device.write8(MPL3115A2_CTRL_REG1, (Barometer.ctrlReg1Data | osr))
		
		else:
			print "*** setOutputSampleRate: osr too large (>=8)"

	#________________________________________________
	def setTimeStep(self, st):
		"""Set ST in CTRL_REG2"""
		
		self.setStandbyMode()
		
		# The ST_Value is set from 0x0 - 0xF, corresponding to steps 1-32,768 seconds
		if st <= 0xF:
			Barometer.ctrlReg2Data = self._device.readU8(MPL3115A2_CTRL_REG2) & 0xF0	# clear ST[3:0]
			self._device.write8(MPL3115A2_CTRL_REG2, (Barometer.ctrlReg2Data | st))
	
		else:
			print "*** setTimeStep: st too large (>15)"

	#________________________________________________
	def setPressureEventFlag(self):
		"""Enable internal event flag upon detection of new Pressure data"""
		
		# Once configured, event flag can be monitored by reading STATUS register (polling or interrupt)
		self.setStandbyMode()
		self._device.write8(MPL3115A2_PT_DATA_CFG, MPL3115A2_PT_DATA_CFG_PDEFE)

	#________________________________________________
	def getPressure(self):
		"""Get pressure level, in inch of Mercury"""
		# Sensor data returned in Pascals
		
		status = 0
		while (status & MPL3115A2_REGISTER_STATUS_PDR) != MPL3115A2_REGISTER_STATUS_PDR:
			status = self._device.readU8(MPL3115A2_REGISTER_STATUS)
			time.sleep(0.01)
		
		pressureMSB = self._device.readU8(MPL3115A2_REGISTER_PRESSURE_MSB)
		pressureCSB = self._device.readU8(MPL3115A2_REGISTER_PRESSURE_CSB)
		pressureLSB = self._device.readU8(MPL3115A2_REGISTER_PRESSURE_LSB)
		
		pressure = ((pressureMSB<<16) + (pressureCSB<<8) + pressureLSB) / 64.0
#		pressureHg = pressure * 0.0002953006		# 1 Pascal = 0.0002953006 inch mercury (32 deg F)
		pressureHg = pressure * 0.0002961			# 1 Pascal = 0.000296134  inch mercury (60 deg F)
		return pressureHg

	#________________________________________________
	def getPressureDelta(self):
		"""Get pressure difference from last sample, in inch of Mercury"""
		# Sensor data returned in Pascals
		
		pressureDeltaMSB = self._device.readU8(MPL3115A2_OUT_P_DELTA_MSB)
		pressureDeltaCSB = self._device.readU8(MPL3115A2_OUT_P_DELTA_CSB)
		pressureDeltaLSB = self._device.readU8(MPL3115A2_OUT_P_DELTA_LSB)
		
		pressureDelta = ((pressureDeltaMSB<<16) + (pressureDeltaCSB<<8) + pressureDeltaLSB)
		if pressureDeltaMSB > 0x7F:
			pressureDelta = ~pressureDelta & 0xF0
			pressureDelta = -pressureDelta / 64.0
		
		else:
			pressureDelta = pressureDelta / 64.0
		
#		pressureDeltaHg = pressureDelta * 0.0002953006		# 1 Pascal = 0.0002953006 inch mercury (32 deg F)
		pressureDeltaHg = pressureDelta * 0.0002961			# 1 Pascal = 0.000296134  inch mercury (60 deg F)
		return pressureDeltaHg

	#________________________________________________
	def getAltitude(self):
		"""Get altitude, in feet"""
		# Sensor data returned in meters
		
		status = 0
		while (status & MPL3115A2_REGISTER_STATUS_PDR) != MPL3115A2_REGISTER_STATUS_PDR:
			status = self._device.readU8(MPL3115A2_REGISTER_STATUS)
			time.sleep(0.01)
		
		altitudeMSB = self._device.readU8(MPL3115A2_REGISTER_PRESSURE_MSB)
		altitudeCSB = self._device.readU8(MPL3115A2_REGISTER_PRESSURE_CSB)
		altitudeLSB = self._device.readU8(MPL3115A2_REGISTER_PRESSURE_LSB)
		
		altitudeM = ((altitudeMSB<<24) + (altitudeCSB<<16) + (altitudeLSB<<8)) / 65536
		altitudeFt = altitudeM * 3.28084
		return altitudeFt

	#________________________________________________
	def getAltitudeDelta(self):
		"""Get altitude difference from last sample, in feet"""
		# Sensor data returned in meters
		
		altitudeDeltaMSB = self._device.readU8(MPL3115A2_OUT_P_DELTA_MSB)
		altitudeDeltaCSB = self._device.readU8(MPL3115A2_OUT_P_DELTA_CSB)
		altitudeDeltaLSB = self._device.readU8(MPL3115A2_OUT_P_DELTA_LSB)
		
		altitudeDeltaM = (altitudeDeltaMSB<<24) + (altitudeDeltaCSB<<16) + (altitudeDeltaLSB<<8)
		if altitudeDeltaMSB > 0x7F:
			altitudeDeltaM = ~altitudeDeltaM & 0xF0
			altitudeDeltaM = -altitudeDeltaM / 65536.0
		
		else:
			altitudeDeltaM = altitudeDeltaM / 65536
		
		altitudeDeltaFt = altitudeDeltaM * 3.28084
		return altitudeDeltaFt

	#________________________________________________
	def getTemperature(self):
		"""Get temperature, in deg F"""
		# Sensor data returned in deg C
		
		temperatureMSB = self._device.readU8(MPL3115A2_REGISTER_TEMP_MSB)
		temperatureLSB = self._device.readU8(MPL3115A2_REGISTER_TEMP_LSB)
		
		temperatureC = ((temperatureMSB<<8) + temperatureLSB) / 256
		temperatureF = temperatureC * 1.8  + 32.0
		return temperatureF

	#________________________________________________
	def getTemperatureDelta(self):
		"""Get temperature difference from last sample, in deg F"""
		# Sensor data returned in deg C
		
		temperatureDeltaMSB = self._device.readU8(MPL3115A2_OUT_T_DELTA_MSB)
		temperatureDeltaLSB = self._device.readU8(MPL3115A2_OUT_T_DELTA_LSB)
		
		temperatureDeltaC = ((temperatureDeltaMSB<<8) + temperatureDeltaLSB)
		if temperatureDeltaMSB > 0x7F:
			temperatureDeltaC = ~temperatureDeltaC & 0xF0
			temperatureDeltaC = -temperatureDeltaC / 256.0
		
		else:
			temperatureDeltaC = temperatureDeltaC / 256.0
		
		temperatureDeltaF = temperatureDeltaC * 1.8
		return temperatureDeltaF
