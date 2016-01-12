import sys
import time
import usb.core
import usb.util
from lr4 import LR4


# find our device
for dev in usb.core.find(find_all=True,idVendor=0x0417, idProduct=0xdd03):
  print dev

sys.exit()
# was it found?
if dev is None:
    raise ValueError('Device not found')

print dev
# set the active configuration. With no arguments, the first
# configuration will be the active one
sys.exit()
dev.set_configuration()


#    INTERFACE 0: Human Interface Device ====================
#     bLength            :    0x9 (9 bytes)
#     bDescriptorType    :    0x4 Interface
#     bInterfaceNumber   :    0x0
#     bAlternateSetting  :    0x0
#     bNumEndpoints      :    0x2
#     bInterfaceClass    :    0x3 Human Interface Device
#     bInterfaceSubClass :    0x0
#     bInterfaceProtocol :    0x0
#     iInterface         :    0x0 
#      ENDPOINT 0x81: Interrupt IN ==========================
#       bLength          :    0x7 (7 bytes)
#       bDescriptorType  :    0x5 Endpoint
#       bEndpointAddress :   0x81 IN
#       bmAttributes     :    0x3 Interrupt
#       wMaxPacketSize   :    0x8 (8 bytes)
#       bInterval        :   0x32
#      ENDPOINT 0x2: Interrupt OUT ========

#we want configuration 0 interface 0

# get an endpoint instance
cfg = dev.get_active_configuration()
intf = cfg[(0,0)]

ep_out = usb.util.find_descriptor(
    intf,
    # match the first OUT endpoint
    custom_match = \
    lambda e: \
        usb.util.endpoint_direction(e.bEndpointAddress) == \
        usb.util.ENDPOINT_OUT)


ep_in = usb.util.find_descriptor(
    intf,
    # match the first OUT endpoint
    custom_match = \
    lambda e: \
        usb.util.endpoint_direction(e.bEndpointAddress) == \
        usb.util.ENDPOINT_IN)
#
#assert ep is not None
#
# write the data

lr4 = LR4(ep_in,ep_out)
print lr4.getSerialNumber()
while True:
  print lr4.measure()  
  time.sleep(0.5)
