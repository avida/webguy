#!/usr/bin/python3
# How to install RPi module:
# sudo apt-get install python3-rpi.gpio


try:
    import RPi.GPIO as GPIO
except ImportError:
    print("Cannot import GPIO")
PORT = 4

class RaspiGPIOOut:

    def __init__(self, port):
        self.port = port
        GPIO.setwarnings(False)
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(port, GPIO.OUT)

    def getValue(self):
        return GPIO.input(self.port)

    def setValue(self, val):
        GPIO.output(self.port, val)

if __name__ == "__main__":
    pin4 = RaspiGPIOOut(PORT)
    if pin4.getValue():
        print("false")
        pin4.setValue(False)
    else:
        pin4.setValue(True)
        print("true")
