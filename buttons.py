#!/usr/bin/env python2.7

import subprocess
import time
import RPi.GPIO as GPIO
import os
import signal
import sys

channel_list = [17, 22, 23, 27]
backlightOn = True
scanRunning = False

def toggleBacklight(channel):
    global backlightOn
    if backlightOn:
        backlightOn = False
        backlight.start(0)
    else:
        backlightOn = True
        backlight.start(100)

def buttonEvent(channel):
    startTime = time.time()
    while GPIO.input(channel) == GPIO.LOW:
        time.sleep(0.02)
    print "Button #%d pressed for %f seconds." % (channel, time.time() - startTime)

def runMorrisMain(channel):
    #startTime = time.time()
    #while GPIO.input(channel) == GPIO.LOW:
    #    time.sleep(0.02)
    ##os.system("bash /home/pi/runScanner.sh")
    #subprocess.Popen("/home/pi/runScanner.sh", shell=True, stdout=subprocess.PIPE)
    global scanRunning
    global scan
    if scanRunning:
        scanRunning = False
        os.killpg(os.getpgid(scan.pid), signal.SIGTERM)
    else:
        scanRunning = True
        scan = subprocess.Popen("/home/pi/runScanner.sh", shell=True, 
                                stdout=subprocess.PIPE, preexec_fn=os.setsid)

def poweroff(channel):
    global backlightOn
    startTime = time.time()
    while GPIO.input(channel) == GPIO.LOW:
        time.sleep(0.02)
    if (time.time() - startTime) > 2:
        #subprocess.call("sudo shutdown -h now", shell=True)
        os.system("sudo shutdown -h now")
    elif backlightOn:
        backlightOn = False
        backlight.start(0)
    else:
        backlightOn = True
        backlight.start(100)

def graceful_exit(signum, frame):
    print "Got an exit signal"
    backlight.stop()
    GPIO.cleanup()
    sys.exit()

# Catch termination signals
signal.signal(signal.SIGINT, graceful_exit)
signal.signal(signal.SIGTERM, graceful_exit)

# Setup
GPIO.setmode(GPIO.BCM)
GPIO.setup(channel_list, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(18, GPIO.OUT)
backlight = GPIO.PWM(18, 1000)
backlight.start(100)

# TODO Maybe make buttons 17 and 22 hardware volume control
#GPIO.add_event_detect(17, GPIO.FALLING, callback=toggleBacklight, bouncetime=200)
GPIO.add_event_detect(22, GPIO.FALLING, callback=toggleBacklight, bouncetime=200)
GPIO.add_event_detect(23, GPIO.FALLING, callback=runMorrisMain, bouncetime=200)
GPIO.add_event_detect(27, GPIO.FALLING, callback=poweroff, bouncetime=200)

while True:
    time.sleep(0.02) # sleep prevents high CPU use

# Execution should never reach this point
backlight.stop()
GPIO.cleanup()
