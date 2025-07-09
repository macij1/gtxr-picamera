# gtxr-picamera
Instructions on setting up the microUSB Serial communication [here](https://github.com/macij1/gtxr-picamera/blob/main/USB-gadgetmode.md)

# env set up in a new Pi zero
check env_setup.sh

## serial mockups
'socat -d -d pty,raw,echo=0 pty,raw,echo=0'
This should output two paths whose inputs and outputs are connected.