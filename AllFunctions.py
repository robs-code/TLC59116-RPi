# Author: Robert E Smith
# Date: 4/28/19
#
# Script to demonstrate all functions of the TLC59116 LED Driver.
# ----------------------------------------------------------
#
#    HOOKUP
# RPi     LED Drivers
# ---     -----------
# 3.3v ->    VCC
# GND  ->    GND
#  2   ->    SDA
#  3   ->    SCL
#  
# Connect an LED's anode(+) to 5V and cathode(-) to pins on the LED drivers.
# Insert a 1k ohm resistor between R-EXT and GND.
# RESET should be pulled to VCC on LEDDriver2 and connected to pin 14 for LEDDriver1.
# Two drivers must be used. Double check you have the same addresses.

import TLC59116
import time
import smbus

bus = smbus.SMBus(1) # Using the Raspberry Pi's I2C Bus Channel 1
LEDDriver1 = TLC59116.TLC59116(0x60, bus,14)
LEDDriver2 = TLC59116.TLC59116(0x61, bus)

LEDDriver1.enable()
LEDDriver2.enable()
LEDDriver1.resetDriver()
LEDDriver2.resetDriver()

while(True):
    # Turn on and off all LEDS and perform an error check & report. 
    # ------------------------------------------------------
    print("\nTurning on all LEDs")
    for i in range(0,16):
        LEDDriver1.LEDOn(i)
        time.sleep(0.1)
    for i in range(0,16):
        LEDDriver2.LEDOn(i)
        time.sleep(0.1)

    # checkErrors returns true if there were any problems
    print("\nError Report:")
    print("-----------------------------------------")
    if LEDDriver1.checkErrors() is True:
        LEDDriver1.reportErrors()
    if LEDDriver2.checkErrors() is True:
        LEDDriver2.reportErrors()
        
    print("\nTurning off all LEDs")
    for i in range(0, 16):
        LEDDriver1.LEDOff(i)
        time.sleep(0.1)
    for i in range(0, 16):
        LEDDriver2.LEDOff(i)
        time.sleep(0.1)
        

    # Individually control LEDs brightness
    # ------------------------------------------------------
    print("\nAdjusting indivial LEDs brightness");
    LEDDriver1.LEDPWM(0);
    LEDDriver1.LEDPWM(1);
    for i in range(0, 256):
        LEDDriver1.setPWM(0, i)
        LEDDriver1.setPWM(1,255-i)
        time.sleep(0.005)
    for i in range(255, -1, -1):
        LEDDriver1.setPWM(0, i)
        LEDDriver1.setPWM(1,255-i)
        time.sleep(0.005)
    for i in range(0, 256):
        LEDDriver1.setPWM(0, i)
        LEDDriver1.setPWM(1,255-i)
        time.sleep(0.005)
    for i in range(255, -1, -1):
        LEDDriver1.setPWM(0, i)
        LEDDriver1.setPWM(1,255-i)
        time.sleep(0.005)
 
    # Assign LEDs to a group and control the brightness of the group.
    print("\nAdjusting group brightness")
    for i in range (0,16,2):
        LEDDriver1.LEDGroup(i)
        
    for i in range(0,256):
        LEDDriver1.setGroupPWM(i)
        time.sleep(0.005)
    for i in range(255, -1, -1):
        LEDDriver1.setGroupPWM(i)
        time.sleep(0.005)

    # Assign LEDs to a group and control the blinking and duty cycle (%ON/OFF).
    print("\nAssign 1 second group blink frequency and adjust duty cycle")
    print("-----------------------------------------")
    for i in range (0,16):
        LEDDriver1.LEDGroup(i)
        
    for i in range(64,256, 64):
        print("Duty Cycle: " + str((i+1)/256) + "%")
        LEDDriver1.SetGroupBlink(47,i)
        time.sleep(4)
        
    LEDDriver1.resetDriver()
    LEDDriver2.resetDriver()
        
