#!/usr/bin/python
import usb
import time
import sys

'''
Copyright (c) 2016 Troy Denton

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
'''



'''
Python class for reading LR4 sensor from porcupine labs
'''

class LR4(object):

  '''
  usb details
  '''
  ID_VENDOR=0x0417
  ID_PRODUCT=0xdd03
  INTERFACE_NUM=0
  ENDPOINT_IN=0x81
  ENDPOINT_OUT=0x02
  '''
  OUT Report - Command Packet Defintion

  0x00 - Get Configuration: Generates an IN report packet with current ConfigValue, ConfigInterval, and other status

  0x01 - Set Config: Sets new values into global variables ConfigValue and ConfigInterval
                    Byte [2:1] = New value for ConfigValue
                    Byte [4:3] = New value for ConfigInterval

  0x02 - Write Config: Writes current values for ConfigValue and ConfigInterval to EEPROM

  0x03 - Get Product Info: Gets six bytes from the product information data structure
                    Byte [1] = Offset into Product Info data structure
  '''
  CMD_GET_CONFIG=0x00
  CMD_SET_CONFIG=0x01
  CMD_WRITE_CONFIG=0x02
  CMD_GET_PRODUCT_INFO=0x03
  '''
  IN Report - Status Packet Definition

  0x00 - Distance Measurement: Data sent to host for normal distance measurement mode
				Byte [0] = STS_MEASUREMENT_DATA
				Byte [1] = Measurement in millimeters (lsb)
				Byte [2] = Measurement in millimeters (msb)
				Byte [3] = 0
				Byte [4] = Progress flags (lsb)
				Byte [5] = Progress flags (msb)
				Byte [6] = TLM100 state
				Byte [7] = Sample count
  0x01 - Configuration Data: Sends current values for ConfigValue and ConfigInterval to host
				Byte [0] = STS_CONFIG_DATA
				Byte [1] = ConfigValue (lsb)
				Byte [2] = ConfigValue (msb)
				Byte [3] = IntervalValue (lsb)
				Byte [4] = IntervalValue (msb)
				Byte [5] = 0
				Byte [6] = 0
				Byte [7] = 0
  0x02 - Product Information: Sends a six byte chunk of the product information data structure
				Byte [0] = STS_PRODUCT_INFO
				Byte [1] = Byte offset into product info data structure
				Byte [7:2] = Data bytes
  '''
  STS_MEASUREMENT_DATA=0x00
  STS_CONFIG_DATA=0x01  
  STS_PRODUCT_INFO=0x02

  '''
  :returns: array of usb devices corresponding to the LR4 from porcupine labs
  '''
  @staticmethod
  def _getDevices():
    return map(LR4,list(usb.core.find(find_all=True,idVendor=LR4.ID_VENDOR, idProduct=LR4.ID_PRODUCT)))

  
  @staticmethod
  def listDevices():
    return LR4._getDevices()

  '''
  get device 
  :param serial: the serial number of the device (string).  If not specified, returns the first device found
  : returns LR4: lr4 object, or None if no match was found
  '''
  @staticmethod
  def getDevice(serialNum=None):
    devices=LR4._getDevices()
    if devices != []:
      if serialNum is None:  #return first device found if no serial num specified
        return devices[0]
      else:
        device=None
        for dev in devices:
          if (str(dev.getSerialNumber().strip()) == str(serialNum.strip())):
            device=dev 
            break
          else:
            dev.close()
        return device
    else:
      return None  #no device found

  '''
  Initialize the LR4
  :param dev: usb.Device instance corresponding to the LR4
  '''
  def __init__(self,dev):
    self.usbDeviceHandle=dev.open()
    #self.usbDevice.reset()
    try:
      self.usbDeviceHandle.detachKernelDriver(LR4.INTERFACE_NUM)
    except:
      pass
    self.usbDeviceHandle.claimInterface(LR4.INTERFACE_NUM)
    self._readConfig()
    self._configSingleMode()

  '''
  Close the device
  '''
  def close(self):
    return self.usbDeviceHandle.releaseInterface()

  '''
  Read bytes from the LR4
  :returns: list of 8 bytes as read from the LR4
  '''
  def _read(self):
    #x=self.epin.read(8,timeout=1000)
    #return x
    ret = None
    numFails = 0 
    while (ret is None and numFails < 10):
        try:
            ret = list(self.usbDeviceHandle.interruptRead(LR4.ENDPOINT_IN,8,1000))
        except:
            numFails += 1
    return ret



  '''
  Write to the LR4
  :param arr: array of ints to write to LR4
  '''
  def _write(self,arr):
    return self.usbDeviceHandle.interruptWrite(LR4.ENDPOINT_OUT,bytearray(arr))
 
  '''
  Read in configuration data from the LR4
  '''
  def _readConfig(self):
    cmd = [0]*8
    cmd[0]=LR4.CMD_GET_CONFIG
    self._write(cmd)
    self.config=self._read()
    #config = result[1] + (result[2]<<8) + (status[3]<<16) + (status[4]<<24)
    #return config
    return self.config


  '''
  write configuration to device
  :param cmd: bytearray to write to the device
  '''
  def _writeConfig(self,cmd):
    self._write(cmd)
    self._readConfig()
    #occasionally it seems to get misconfigured?
    # note that equality of cmd and config hinges on the first byte being the same, which is coincidental, but convenient
    while (cmd != self.config): 
      self._write(cmd)
      self._readConfig()
      time.sleep(0.5)

  '''
  set rangefinder to single mode, trigger on run bit
  '''
  def _configSingleMode(self):
    #     [set config          lsb config    msb config              interval
    cfg1 = self.config[1]
    cfg1 &= ~0x10
    cfg1 |= 0x08
    cmd = [LR4.CMD_SET_CONFIG,0x00,0x00,0x00,0x00,0,0,0]
    self._writeConfig(cmd)

    cmd = [0]*8
    cmd[0] = LR4.CMD_WRITE_CONFIG
    self._write(cmd)

  
  '''
  get Serial Number from device
  :returns: serial number string
  '''
  def getSerialNumber(self):
    #get first 6 bytes of PRODUCT_INFO.SERIAL_NUMBER
    cmd=[0]*8
    cmd[0]=LR4.CMD_GET_PRODUCT_INFO
    cmd[1]=70
    self._write(cmd)
    res1=self._read()
    #get next 4 bytes of PRODUCT_INFO.SERIAL_NUMBER
    cmd[1]=76
    self._write(cmd)
    res2=self._read()
    res = res1[2:] + res2[2:5]
    serialNum = ''.join(map(chr,res))
    return serialNum.rstrip(' \t\r\n\0')
      
  '''
  begin a distance measurement
  '''
  def _startMeasurement(self):
    cmd = [LR4.CMD_SET_CONFIG,self.config[1],self.config[2] | 0x80,self.config[3],self.config[4],0,0,0]
    return self._write(cmd)

  '''
  end a distance measurement
  '''
  def _endMeasurement(self):  
    cmd = [LR4.CMD_SET_CONFIG,self.config[1],self.config[2] & ~0x80,self.config[3],self.config[4],0,0,0]
    self._write(cmd)

  '''
  measure - return a measurement 
  :returns: distance in mm, integer value
  '''
  def measure(self):
    self._startMeasurement()
    # read in data
    dat = self._read()
    self._endMeasurement()
    return int(( dat[2]<<8 ) + dat[1])


'''
test output function.  Just a helper for the other test* functions
:param dev: LR4 object to test
'''
def testOutput(dev):
    try:
      print "serial number '%s'"%(dev.getSerialNumber())
      print "\t%d mm"%dev.measure()
    except Exception as e:
      print "\terr" 


'''
test ability to query multiple devices
'''
def testMultiDevices():
  devices = LR4.listDevices()
  #print devices
  for dev in devices:
    if dev is not None:
      testOutput(dev)
      dev.close()
  
'''
test ability to retrieve single device
'''
def testSingleDevice(serial=None):
  if serial is not None:
    dev = LR4.getDevice(serialNum=serial)
  else:
    dev = LR4.getDevice()
  if (dev is not None):
    testOutput(dev)
    dev.close()

class MyError(Exception): pass

if __name__=="__pain__":
#  l = LR4('/dev/hidraw10')
#  print "%s is serial number '%s'"%(dev,l.getSerialNumber())
#  l.close()
#  dev = LR4.getDevice(serialNum = '001980')
#  print dev.getSerialNumber()
#  cmd = [LR4.CMD_SET_CONFIG,0,0x80,dev.config[3],dev.config[4],0,0,0]
#  dev._write(cmd)
#  print dev._readConfig()
#  dat = dev._read()
#  print int(( dat[2]<<8 ) + dat[1])
#  cmd = [LR4.CMD_SET_CONFIG,0,0,dev.config[3],dev.config[4],0,0,0]
#  dev._write(cmd)
#  print dev._readConfig()
    testMultiDevices()

                
                
 
if __name__=="__main__":
    busses = usb.busses()
    for bus in busses:
        for dev in bus.devices:
            #print "%d:%d"%(dev.idVendor,dev.idProduct)
            if (dev.idVendor == LR4.ID_VENDOR and dev.idProduct == LR4.ID_PRODUCT):
                lr4 = LR4(dev)
                print lr4.measure()
                lr4.close()
            elif (False):
                print "found LR4, opening!"
                dh = dev.open()
                print "detach kernel"
                try:
                    dh.detachKernelDriver(LR4.INTERFACE_NUM)
                except:
                    print "\tno detach"
                print "claim"
                dh.claimInterface(LR4.INTERFACE_NUM)
                #TODO do some work
                print "release"
                dh.releaseInterface()
