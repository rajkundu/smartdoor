#!/usr/bin/python3

import RPi.GPIO as GPIO
import time

RELAY_PIN = 23

if(__name__ == "__main__"):
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(RELAY_PIN, GPIO.OUT)
    GPIO.output(RELAY_PIN, True)
    time.sleep(2)
    GPIO.output(RELAY_PIN, False)
    GPIO.cleanup()
