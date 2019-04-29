from gpiozero import LED # RPi.GPIO is being deprecated. gpiozero.LED is used for digital output.
import time

# Register Addresses
TLC_PWM_BASE = 0x02
TLC_GROUP_PWM = 0x12
TLC_GROUP_FREQ = 0x13
TLC_LED_OUTPUT_BASE = 0x14
TLC_ERROR_FLAG1 = 0x1D
TLC_ERROR_FLAG2 = 0x1E
TLC_RESET = 0x6B

# Possible LED Output States
LED_OFF = 0x00
LED_ON = 0x01
LED_PWM = 0x02
LED_GROUP = 0x03

class TLC59116:

  # Initialize the device
  def __init__(self, address, bus, reset=False):
    self.TLC_ADDR = address
    self.bus = bus
    if not reset:
      print("WARNING: Device " + hex(self.TLC_ADDR) + " created without RESET pin declared. LEDs will be turned off during driverReset() in place of a hardware reset.")
    else:
      self.reset = LED(reset)
      self.reset.on()
    self.LEDOUT = [0x00, 0x00, 0x00, 0x00 ] # LED Output states are stored in four registers. Four LEDs are stored in each register.
    self.ERR_FLAG = 0xFFFF
    self.groupMode = 0

  # Send I2C write to the device. Takes a register and command.
  def writeToDevice(self, reg, val):
    try: 
      self.bus.write_byte_data(self.TLC_ADDR, reg, val)
    except IOError:
      print("Could not write to device " + hex(self.TLC_ADDR))

  # Send I2C read to the device. Takes a register.
  def readFromDevice(self, reg):
    try:
      return self.bus.read_byte_data(self.TLC_ADDR, reg)
    except IOError:
      return -1

  # Adjust LEDOUT to reflect current LED Output States
  # --------------------------------------------------------
  def modifyLEDOutputState(self, LED, state) :
    positionInRegister = ((LED % 4) * 2)
    registerLocation = LED // 4

    # Use a mask to change only the specified LED's position
    mask = 0x03 << positionInRegister
    newLEDOUT = self.LEDOUT[registerLocation] | mask
    newLEDOUT = self.LEDOUT[registerLocation] & ~mask
    if (state != 0x00):
        newLEDOUT = self.LEDOUT[registerLocation] | (state << positionInRegister)
    self.LEDOUT[registerLocation] = newLEDOUT

    self.writeToDevice(TLC_LED_OUTPUT_BASE + registerLocation, newLEDOUT)
  
  def LEDOff(self, LED):
    self.modifyLEDOutputState(LED, LED_OFF)
    
  def LEDOn(self, LED):
    self.modifyLEDOutputState(LED, LED_ON)
    
  def LEDPWM(self, LED):
    self.modifyLEDOutputState(LED, LED_PWM)

  def LEDGroup(self, LED):
    self.setPWM(LED, 255)
    self.modifyLEDOutputState(LED, LED_GROUP)
  # --------------------------------------------------------

  # Set brightness for LED
  def setPWM(self, pin, duty):
    self.writeToDevice(TLC_PWM_BASE + pin, duty)

  # Set brightness for the group of LEDs
  def setGroupPWM(self, duty):
    # Check if we are already in Group PWM Mode
    if self.groupMode == 1:
      self.writeToDevice(0x01, 0x00)
      groupMode = 0

    self.writeToDevice(TLC_GROUP_PWM, duty)

  # Set blink frequency for group. Group PWM Register becomes the duty cycle for the blink frequency (%on/off).
  def SetGroupBlink(self, freq, dutyCycle):
    self.setGroupPWM(dutyCycle)
    if self.groupMode == 0:
      self.writeToDevice(0x01, 0x20);
      groupMode = 1;

    self.writeToDevice(TLC_GROUP_FREQ, freq)

  # Two registers are used for indicating channel errors. Handle the clearing, checking, and reporting of theses errors.
  # --------------------------------------------------------
  def clearErrors(self):
    self.writeToDevice(0x01, 0x80)
    self.writeToDevice(0x01, 0x00)

  def checkErrors(self):
    flag1 = self.readFromDevice(TLC_ERROR_FLAG1)
    flag2 = self.readFromDevice(TLC_ERROR_FLAG2)
    self.ERR_FLAG = (flag2 << 8) + flag1
    if self.ERR_FLAG == 0xFFFF:
      return False
    return True

  def reportErrors(self):
    if self.ERR_FLAG == 0xFFFF:
      print("No errors detected.")
      return False
    elif self.ERR_FLAG == -0x101:
      print("Could not read from device: "+ hex(self.TLC_ADDR)) 
    else:
      for i in range(0,16):
        if (not((self.ERR_FLAG >> i) & 0x1)):
          print("Device " + hex(self.TLC_ADDR)+ ": LED " + str(i) + " disconnected/overheated")
    self.clearErrors()
  # --------------------------------------------------------

  # Start up the driver in a fresh state
  def enable(self):
    self.writeToDevice(0x00, 0x80)

  # Reset the driver either by the RESET pin, and if it was not defined just turn off all the LEDs.
  def resetDriver(self):
    self.LEDOUT = [0x00, 0x00, 0x00, 0x00 ]
    try:
      self.reset
    except AttributeError:
      self.turnOffAllLEDs()
    else:
      self.reset.off()
      time.sleep(0.001) # Allow a microsecond for the device to power down.
      self.reset.on()
      self.LEDOUT = [0x00, 0x00, 0x00, 0x00 ]
    self.enable()
     
  # Nice function to turn off all LED channels.
  def turnOffAllLEDs(self):
    for i in range(0,16):
      self.LEDOff(i)

  # !NOT RECOMMENDED! resetDriver() is preferred. Software reset over I2C. Restarts all TLC59116 devices on I2C bus. This must be followed by turnOffAllLEDs for each device.
  def resetAllTLCs(self):
    self.bus.write_byte_data(0x6B, 0xA5, 0x5A)






