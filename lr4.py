#!/usr/bin/python
import subprocess
import time
'''
Python class for reading LR4 sensor
'''

class LR4(object):

  '''
  communication defines
  '''
  CMD_GET_CONFIG=0x00
  CMD_SET_CONFIG=0x01
  CMD_WRITE_CONFIG=0x02
  CMD_GET_PRODUCT_INFO=0x03

  '''
  get devices that match our laser rangefinder via dmesg.
 
  yes this is greasy.  but a stopgap until a more elegant solution is found
  :returns: array of hidraw devices likely to be our LR4 device
  '''
  @staticmethod
  def _getHIDRawDevices():
    cmd="dmesg | grep 'Porcupine Electronics LR4' | grep -vi keyboard | sed -ne 's/.*hidraw\([^:]*\).*/\\1/p' | sort | uniq"
    output=subprocess.check_output(cmd,shell=True)
    lines=str.split(output,'\n')
    linesHIDRaw=[]
    for line in lines:
      if line != "":
        linesHIDRaw.append("/dev/hidraw%s"%line.rstrip())
    return linesHIDRaw

  
  @staticmethod
  def listDevices():
    return LR4._getHIDRawDevices()

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
  def __init__(self,filename):
    self.fh = open(filename,"wb+")
    self._readConfig()
    self._configSingleMode()

  '''
  Close the filehandle associated with the LR4
  '''
  def close(self):
    return self.fh.close()

  '''
  Read from the LR4
  '''
  def _read(self):
    return map(ord,self.fh.read(8))

  '''
  read raw bytes 
  '''
  def _readBytes(self):
    return self.fh.read(8)

  '''
  Write to the LR4
  :param arr: array of ints to write to LR4
  '''
  def _write(self,arr):
    return self.fh.write(bytearray(arr))
 
  '''
  Read in configuration data from the LR4
  '''
  def _readConfig(self):
    cmd = [0]*8
    cmd[0]=LR4.CMD_GET_CONFIG
    self._write(cmd)
    self.config=self._read()
    return self.config
    #print self.config
    #config = result[1] + (result[2]<<8) + (status[3]<<16) + (status[4]<<24)
    #return config


  '''
  write configuration to device
  '''
  def _writeConfig(self,cmd):
    self._write(cmd)
    self._readConfig()
    #occasionally it seems to get misconfigured?
    # note that equality of cmd and config hinges on the first byte being the same, which is coincidental, but convenient
    while (cmd != self.config): 
      self._write(cmd)
      self._readConfig()
      time.sleep(0.1)

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
  print devices
  for dev in devices:
    try:
      l = LR4(dev)
      print "%s is serial number '%s'"%(dev,l.getSerialNumber())
      print "\t%d mm"%l.measure()
      l.close()
    except IndexError as e:
      print "\tfuck" 
