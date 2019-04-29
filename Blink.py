# Author: Robert E Smith
# Date: 4/28/19
#
# Script to perform a simple blink by turning an LED on and off.
# ----------------------------------------------------------
#
#    HOOKUP
# RPi     LED Driver
# ---     ----------
# 3.3v ->    VCC
# GND  ->    GND
#  2   ->    SDA
#  3   ->    SCL
#
# Connect an LED's anode(+) to 5V to and cathode(-) to pin 0 on the LED driver.
# Insert a 1k ohm resistor between R-EXT and GND.
# RESET can be pulled high to VCC if it is not going to be used.

import TLC59116
import time
import smbus

bus = smbus.SMBus(1) # Using I2C Channel 1 (Pins 2 & 3)
LEDDriver = TLC59116.TLC59116(0x61, bus)


LEDDriver.enable() # Required to start up the board
LEDDriver.resetDriver() # Guarantees a fresh start


while(True):
    LEDDriver.LEDOn(0)
    time.sleep(1)
    LEDDriver.LEDOff(0)
    time.sleep(1)
