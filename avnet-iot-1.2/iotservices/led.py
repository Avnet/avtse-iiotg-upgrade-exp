#!/usr/bin/env python

from subprocess import call
from time import sleep
import threading

ApMode = False
GreenThisTime = False
RedThisTime = False

GREEN_LED = '/sys/class/leds/green/brightness'
RED_LED = '/sys/class/leds/red/brightness'

def green_led_on():
    with open(GREEN_LED, 'w') as f:
        f.write('1\n')
    print("GON")

def green_led_off():
    with open(GREEN_LED, 'w') as f:
        f.write('0\n')
    print("GOF")

def red_led_on():
    with open(RED_LED, 'w') as f:
        f.write('1\n')
    print("RON")

def red_led_off():
    with open(RED_LED, 'w') as f:
        f.write('0\n')
    print("ROF")

def get_ap_mode():
    global ApMode
    try:
        hostapd = call(['systemctl', 'is-active', 'hostapd.service'], stdout=None , stderr=None)
        ApMode = hostapd == 0
    except Exception as ex:
        print(ex)
        ApMode = False
    print("AP status" + str(ApMode))
    return ApMode

def check_switch():
    global GreenThisTime
    global RedThisTime
    global ApMode
    GreenFirst = True
    sleep(3)
    try:
        while 1:
            get_ap_mode()
            sleep(1)
            if ApMode:
                if RedThisTime:
                    RedThisTime = False
                    red_led_off()
                    green_led_on()
                else:
                    RedThisTime = True
                    green_led_off()
                    red_led_on()
            else:
                if GreenFirst:
                    red_led_off()
                    GreenFirst = False
                if GreenThisTime:
                    GreenThisTime = False
                    green_led_on()
                else:
                    GreenThisTime = True
                    green_led_off()
    except Exception as ex:
        print(ex)

if __name__ == '__main__':
    print("Starting LED service")
    ApMode = True
    red_led_off()
    green_led_on()
    GreenThisTime = True
    t2 = threading.Thread(name='child procs', target=check_switch)
    t2.start()
    while True:
        sleep(60*60)
    red_led_off()
    green_led_off()
