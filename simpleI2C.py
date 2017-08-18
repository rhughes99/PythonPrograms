"""
Short example of something.

Last touched: 08/16/2017
"""

from Adafruit_I2C import Adafruit_I2C


#i2c = Adafruit_I2C(0x18,-1,True)
i2c = Adafruit_I2C(0x18,2,True)

print "--- (1) address= 0x%X  errMsg= %s" % (i2c.address, i2c.errMsg())

byte = i2c.readU8(0)

print "--- (2) address= 0x%X  errMsg= %s  byte= %d" % (i2c.address, i2c.errMsg(), byte)

