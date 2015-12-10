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
    #config = result[1] + (result[2]<<8) + (status[3]<<16) + (status[4]<<24)
    #return config
 
  def enableMeasurements(self):
    cmd = [LR4.CMD_SET_CONFIG,self.config[1],self.config[2] | 0x80,self.config[3],self.config[4],0,0,0]
    self.write(cmd)
      
  def disableMeasurements(self):  
    cmd = [LR4.CMD_SET_CONFIG,self.config[1],self.config[2] & ~0x80,self.config[3],self.config[4],0,0,0]
    self.write(cmd)


  def measure(self):
    #self.enableMeasurements()
    # read in data
    dat = self.read()
    #self.disableMeasurements()
    return int(( dat[2]<<8 ) + dat[1])

if __name__=="__main__":
  lr4 = LR4("/dev/hidraw5")
  try:
    lr4.enableMeasurements()
    while True:
      print "%d mm"%lr4.measure()
  except KeyboardInterrupt:
    lr4.disableMeasurements()
    lr4.close()
  print "See ya"
