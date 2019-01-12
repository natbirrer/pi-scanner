#!/usr/bin/env python2.7

import subprocess
import time
import RPi.GPIO as GPIO
import os
import signal
import sys
import alsaaudio as audio

channel_list = [17, 22, 23, 27]
backlightOn = True
scanRunning = False

# Setup audio control
mixer = audio.Mixer('PCM')
vol = mixer.getvolume()[0]

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

def volumeUp(channel):
    global vol
    global mixer
    if vol < 100:
        vol += 5 # TODO: volume maps nonlinearly
        mixer.setvolume(vol)
        vol = mixer.getvolume()[0]

def volumeDown(channel):
    global vol
    global mixer
    if vol > 0:
        vol -= 5 # TODO: volume maps nonlinearly
        mixer.setvolume(vol)
        vol = mixer.getvolume()[0]

def gracefulExit(signum, frame):
    print "Got an exit signal"
    backlight.stop()
    GPIO.cleanup()
    sys.exit()

# Catch termination signals
signal.signal(signal.SIGINT, gracefulExit)
signal.signal(signal.SIGTERM, gracefulExit)

# Setup GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setup(channel_list, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(18, GPIO.OUT)
backlight = GPIO.PWM(18, 1000)
backlight.start(100)

# TODO Make volume control buttons linear, not log scale!
GPIO.add_event_detect(17, GPIO.FALLING, callback=volumeUp, bouncetime=200)
GPIO.add_event_detect(22, GPIO.FALLING, callback=volumeDown, bouncetime=200)
GPIO.add_event_detect(23, GPIO.FALLING, callback=runMorrisMain, bouncetime=200)
GPIO.add_event_detect(27, GPIO.FALLING, callback=poweroff, bouncetime=200)

while True:
    time.sleep(0.02) # sleep prevents high CPU use

# Execution should never reach this point
backlight.stop()
GPIO.cleanup()
