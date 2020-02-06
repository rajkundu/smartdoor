#!/usr/bin/python3

import sys
import subprocess
import time
import threading

import touchphat
import RPi.GPIO as GPIO

#-------------------------------#
bt_addrs = {
    "Raj's iPhone":"F4:0F:24:87:61:4C",
    "Christian's iPhone":"E4:E4:AB:3D:3A:4A"
}

lockedLeds = (0, 1)
unlockedLeds = (5, 4)
autoModeLeds = (2, 3)

RELAY_PIN = 23

SERVO_PIN = 18
LOCK_POS_DUTY_CYCLE = 11.0
UNLOCK_POS_DUTY_CYCLE = 5.5
#-------------------------------#

presences = []
threads = []
locked = False
moving = False
kill = False
autoModeEnabled = False
pressed = [False, False, False, False, False, False]
present = False
present_last = False
pwm = None

def updateLights():
    global locked
    global present
    global autoModeEnabled

    for i in lockedLeds:
        touchphat.set_led(i, locked)
    for i in unlockedLeds:
        touchphat.set_led(i, not locked)
    for i in autoModeLeds:
        touchphat.set_led(i, autoModeEnabled)

def lock():
    global pwm
    global locked
    global moving
    global autoModeEnabled
    moving = True

    print("Locking...")
    touchphat.all_off()

    GPIO.output(RELAY_PIN, True)
    pwm.ChangeDutyCycle(LOCK_POS_DUTY_CYCLE)
    for i in range(5, -1, -1):
        if(i == 0):
            pwm.ChangeDutyCycle(0)
        elif(i == 1):
            GPIO.output(RELAY_PIN, False)
        time.sleep(0.2)
        touchphat.led_on(i)
        if(i > 0 and i < 5):
            if(autoModeEnabled and i + 1 in autoModeLeds):
                pass
            else:
                touchphat.led_off(i + 1)
    
    locked = True
    updateLights()
    print("Door \033[91mLOCKED\033[0m")
    moving = False

def unlock():
    global pwm
    global locked
    global moving
    global autoModeEnabled
    moving = True
    
    print("Unlocking...")
    touchphat.all_off()

    GPIO.output(RELAY_PIN, True)
    pwm.ChangeDutyCycle(UNLOCK_POS_DUTY_CYCLE)
    for i in range(6):
        if(i == 5):
            pwm.ChangeDutyCycle(0)
        elif(i == 4):
            GPIO.output(RELAY_PIN, False)
        time.sleep(0.2)
        touchphat.led_on(i)
        if(i > 0 and i < 5):
            if(autoModeEnabled and i - 1 in autoModeLeds):
                pass
            else:
                touchphat.led_off(i - 1)
    
    locked = False
    print("Door \033[92mUNLOCKED\033[0m")
    updateLights()
    moving = False

def setAutoMode(val):
    global autoModeEnabled
    global present
    autoModeEnabled = val
    if(autoModeEnabled):
        if(present and locked):
            unlock()
        elif(not present and not locked):
            lock()
        print("AUTO MODE ENABLED")
    else:
        print("AUTO MODE DISABLED")
    updateLights()

def handle_button_press(button_id):
    global locked
    global autoModeEnabled
    global pressed
    print("Button " + str(button_id) + " pressed")
    if(button_id in unlockedLeds):
        if(autoModeEnabled):
            setAutoMode(False)
        if(locked):
            unlock()
    elif(button_id in lockedLeds):
        if(autoModeEnabled):
            setAutoMode(False)
        if(not locked):
            lock()
    elif(button_id in autoModeLeds):
        #Only execute auto mode toggling if no other buttons are being pressed simultaneously
        anyAutoLedPressed = False
        for i in autoModeLeds:
            if(pressed[i]):
                anyAutoLedPressed = True
                break
        if(not anyAutoLedPressed):
            setAutoMode(not autoModeEnabled)

@touchphat.on_touch([0, 1, 2, 3, 4, 5])
def handle_side_touch(event):
    global moving
    if(moving):
        return
    global pressed
    handle_button_press(event.channel)
    pressed[event.channel] = True

@touchphat.on_release([0, 1, 2, 3, 4, 5])
def handle_side_touch(event):
    global moving
    if(moving):
        return
    global pressed
    pressed[event.channel] = False

#-------------------------------#

def updatePresence(index, bt_addr):
    while(not kill):
        p = subprocess.Popen(["sudo", "timeout", "4", "l2ping", "-c", "1", bt_addr], stdin=subprocess.DEVNULL, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        output = ""
        while(p.poll() is None):
            output += p.stdout.readline().decode("utf-8")
            if output and "Can't connect" not in output:
                presences[index] = True
                break
            else:
                presences[index] = False


def doorHandler(bt_addrs):
    global threads
    global presences
    global autoModeEnabled
    global present
    global present_last
    global kill
    global pwm

    i = 0
    for deviceName in bt_addrs.keys():
        presences.append(False)
        threads.append(threading.Thread(target=updatePresence, args=(i, bt_addrs[deviceName])))
        threads[i].start()
        i += 1

    touchphat.all_off()
    setAutoMode(True)

    while(True):
        try:
            present = False
            for p in presences:
                if(p):
                    present = True
                    break
            
            print("Present: " + str(present))
            
            if(autoModeEnabled):
                if(locked and present and not present_last):
                    unlock()
                elif(not locked and not present and present_last):
                    lock()
            
            present_last = present
            time.sleep(0.5)
        except KeyboardInterrupt:
            print("Turning LEDs off")
            touchphat.all_off()
            
            kill = True
            GPIO.setmode(GPIO.BCM)
            pwm.stop()
            GPIO.cleanup()

            print("Quitting")
            raise

if(__name__ == "__main__"):
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(RELAY_PIN, GPIO.OUT)
    GPIO.setup(SERVO_PIN, GPIO.OUT)
    pwm = GPIO.PWM(SERVO_PIN, 50)
    pwm.start(0)
    doorHandler(bt_addrs)
