#lr4.py
Basic python interface for single-shot measurements from Porcupine Labs LR4 unit

##Prerequisites

Need to install pyusb 1.0 or greater!

pip install --pre pyusb

##Device Permissions
You will either need to run your program as root, or add a udev rule:
###/etc/udev/rules.d/laser.rules
`ACTION=="add",SUBSYSTEMS=="usb",ATTRS{idVendor}=="0417",ATTRS{idProduct}=="dd03",GROUP="plugdev"`

make sure to add yourself to the `plugdev` group:
`sudo usermod -aG plugdev <your username>`

##Known working environments
Currently tested/working on ubuntu desktop 14.04 LTS 64 bit, python 2.7.  Running `python lr4.py` will perform a test of the module (ensure you have followed the directions under *Device Permissions* and have an LR4 unit plugged in)
