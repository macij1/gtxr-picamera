# Connecting to the headless Pi using a microUSB

If the Pi is already set-up for USB serial communication, just create a serial connection after plugging the Pi to your laptop with the microUSB.

in macOS: `screen /dev/tty.usbmodemXXXX 115200`


I followed this tutorial: https://learn.adafruit.com/turning-your-raspberry-pi-zero-into-a-usb-gadget/serial-gadget.

Here's the process I went through. Instead of using a console cable, I ssh'd the first time through a WiFi LAN.

## 1. Flash the SD card

- In the imager's settings, set hostname, username and password, as well as the LAN's details.
- Modify 2 files in boot: config.txt and cmdline.txt as in:
https://learn.adafruit.com/turning-your-raspberry-pi-zero-into-a-usb-gadget/serial-gadget#step-1-edit-config-dot-txt-and-cmdline-dot-txt-2570331

## 2. First console access

We need one initial console access to the Pi to set up the USB gadget mode:

- Option 1: Console cable (serial USB): https://learn.adafruit.com/adafruits-raspberry-pi-lesson-5-using-a-console-cable/connect-the-lead
    
- Option 2: SSH to the Pi over a LAN
    **Make sure to set up SSID and password when flashing**
    Options:
    
    1. This should work straightaway:
        
        `ssh gtxr@raspberrypi.local`
        
    2. If not, figure out the IP of the WiFI interface, should be under `en0`
        
        `ifconfig`
        
        nmap the network with something like:
        
        `nmap -sn {LAN's IP}/mask`
        
        For all detected hosts (only a few hopefully) try to ssh:
        
        `ssh gtxr@10.52.131.48`
       
  ## 3. Follow the rest of the steps to set-up the USB gadget mode
  
  On every Pi’s reboot, a new serial connection should be available under /dev/tty.usbmodem{XXXX}:
  
  `screen /dev/tty.usbmodemXXXX 115200`
