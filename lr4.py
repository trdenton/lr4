#!/usr/bin/python
import time
'''
Python class for reading LR4 sensor
'''

class LR4:

  '''
  communication defines
  '''
  CMD_GET_CONFIG=0x00
  CMD_SET_CONFIG=0x01
  CMD_WRITE_CONFIG=0x02

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
  lr4 = LR4("/dev/hidraw5")
  print "%d mm"%lr4.measure()
  lr4.close()
