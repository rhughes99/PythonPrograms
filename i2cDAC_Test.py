"""
Test code for MCP4725 DAC.

Last touched: 08/18/2017
"""

import numpy as np
import time
import os
import sys

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))

if ROOT_DIR not in sys.path:
    sys.path.append(ROOT_DIR)
import MCP4725

dac = MCP4725.DAC()

sig = lambda t: 50*np.sin(t*5*2*np.pi) +50
start_time = time.time()

while True:
    dac.set_voltage(sig(time.time()-start_time))

