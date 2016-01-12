#!/usr/bin/python
import usb
import subprocess
import time
'''
Python class for reading LR4 sensor
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
  communication defines
  '''
  CMD_GET_CONFIG=0x00
  CMD_SET_CONFIG=0x01
  CMD_WRITE_CONFIG=0x02
  CMD_GET_PRODUCT_INFO=0x03

  '''
 
  :returns: array of usb devices likely to be our LR4 device
  '''
  @staticmethod
  def _getDevices():
    return map(LR4,list(usb.core.find(find_all=True,idVendor=LR4.ID_VENDOR, idProduct=LR4.ID_PRODUCT)))

  
  @staticmethod
  def listDevices():
    return LR4._getDevices()

  '''
  get device by serial number
  :param serial: the ascii serial number of the device
  : returns LR4: lr4 object, or None if no match was found
  '''
  @staticmethod
  def getDevice(serialNum):
    hids=LR4._getHIDRawDevices()
    device=None
    for h in hids:
      device=LR4(h)
      if (str(device.getSerialNumber().strip()) == str(serialNum.strip())):
        break
      else:
        device.close()
        device=None 
      
    return device

  '''
  Initialize the LR4
  :param filename: the filehandle of the hidraw device used by the LR4
  '''
  def __init__(self,dev):
    self.usbDevice=dev
    self.usbDevice.reset()
    if(self.usbDevice.is_kernel_driver_active(LR4.INTERFACE_NUM)):
      self.usbDevice.detach_kernel_driver(LR4.INTERFACE_NUM)
    #self.usbDevice.set_configuration()
    self._readConfig()
    self._configSingleMode()

  '''
  Close the filehandle associated with the LR4
  '''
  def close(self):
    self.usbDevice.reset()
    self.usbDevice.releaseInterface()
    #return self.usbDevice.attach_kernel_driver(LR4.INTERFACE_NUM)

  '''
  Read from the LR4
  '''
  def _read(self):
    #x=self.epin.read(8,timeout=1000)
    #return x
    return list(self.usbDevice.read(LR4.ENDPOINT_IN,8,timeout=1000))


  '''
  read raw bytes 
  '''
  def _readBytes(self):
    return list(self.usbDevice.read(LR4.ENDPOINT_IN,8,timeout=1000))

  '''
  Write to the LR4
  :param arr: array of ints to write to LR4
  '''
  def _write(self,arr):
    return self.usbDevice.write(LR4.ENDPOINT_OUT,bytearray(arr))
 
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
  '''
  def _writeConfig(self,cmd):
    self._write(cmd)
    self._readConfig()
    #occasionally it seems to get misconfigured?
    # note that equality of cmd and config hinges on the first byte being the same, which is coincidental, but convenient
    while (cmd != self.config): 
#      print "CMD"
#      print cmd
#      print type(cmd)
#      print "CFG"
#      print self.config
#      print type(self.config)
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
    cmd = [LR4.CMD_SET_CONFIG,0b00001000,0x00,0x00,0x00,0,0,0]
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
    res1=self._readBytes()
    #get next 4 bytes of PRODUCT_INFO.SERIAL_NUMBER
    cmd[1]=76
    self._write(cmd)
    res2=self._readBytes()

    res = res1[2:] + res2[2:5]

    return str(res).rstrip(' \t\r\n\0')
      
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

if __name__=="__main__":
#  l = LR4('/dev/hidraw10')
#  print "%s is serial number '%s'"%(dev,l.getSerialNumber())
#  l.close()
  devices = LR4.listDevices()
  #print devices
  for (i,dev) in enumerate(devices):
    try:
      print "%s: serial number '%s'"%(i,dev.getSerialNumber())
      print "\t%d mm"%dev.measure()
    except IndexError as e:
      print "\tfuck" 
