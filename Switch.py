import os
import RPi.GPIO as GPIO

def init_Switch():
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(6, GPIO.IN)


if __name__== '__main__':
    init_Switch()

    if GPIO.input(6) == 1:
        os.system("python3 Collector.py")