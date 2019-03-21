import os
import RPi.GPIO as GPIO

count=0

def init_Switch():
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(6, GPIO.IN)


if __name__== '__main__':
    print("This is switch for operating & communicating sensor.")
    print("Please push the button! :)")
    init_Switch()
    while True:
        if GPIO.input(6) == 1:
            os.system("xdotool key ctrl+shift+n")
            os.system("python3 Collector.py")
            count+=1
            if count == 1:
                os.system("python3 Switch.py")