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

  def __init__(self,filename):
    self.fh = open(filename,"wb+")
    self.readConfig()
    self.configSingleMode()


  def close(self):
    self.fh.close()

  def read(self):
    return map(ord,self.fh.read(8))

  def write(self,arr):
    self.fh.write(bytearray(arr))
 
  def readConfig(self):
    cmd = [0]*8
    cmd[0]=LR4.CMD_GET_CONFIG
    self.write(cmd)
    self.config=self.read()
    #print self.config
    #config = result[1] + (result[2]<<8) + (status[3]<<16) + (status[4]<<24)
    #return config


  '''
  write configuration - expects array config
  '''
  def writeConfig(self,cmd):
    self.write(cmd)
    self.readConfig()
    #occasionally it seems to get misconfigured?
    # note that equality of cmd and config hinges on the first byte being the same, which is coincidental, but convenient
    while (cmd != self.config): 
      self.write(cmd)
      self.readConfig()
      time.sleep(0.1)

  '''
  set rangefinder to single mode, trigger on run bit
  '''
  def configSingleMode(self):
    #     [set config          lsb config    msb config              interval
    cfg1 = self.config[1]
    cfg1 &= ~0x10
    cfg1 |= 0x08
    cmd = [LR4.CMD_SET_CONFIG,0b00001000,0x00,0x00,0x00,0,0,0]
    self.writeConfig(cmd)

    cmd = [0]*8
    cmd[0] = LR4.CMD_WRITE_CONFIG
    self.write(cmd)

      
  def startMeasurement(self):
    cmd = [LR4.CMD_SET_CONFIG,self.config[1],self.config[2] | 0x80,self.config[3],self.config[4],0,0,0]
    self.write(cmd)

  def endMeasurement(self):  
    cmd = [LR4.CMD_SET_CONFIG,self.config[1],self.config[2] & ~0x80,self.config[3],self.config[4],0,0,0]
    self.write(cmd)


  def measure(self):
    self.startMeasurement()
    # read in data
    dat = self.read()
    self.endMeasurement()
    return int(( dat[2]<<8 ) + dat[1])

if __name__=="__main__":
  lr4 = LR4("/dev/hidraw5")
  print "%d mm"%lr4.measure()
  lr4.endMeasurement()
  lr4.close()
