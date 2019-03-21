import os
import RPi.GPIO as GPIO


def init_Switch():
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(6, GPIO.IN)


if __name__== '__main__':
    print("This is switch for operating sensor.")
    print("Please push the button! :)")
    init_Switch()
    while True:
        if GPIO.input(6) == 1:
            print("===== Operating Sensor =====")
            os.system("python3 Collector.py")