#!/usr/bin/env python

import os
import threading
from time import sleep

def cat(filename):
    with open(filename) as f:
        f.read()

def check_switch_short(lock):
    try:
    	while 1:
            cat("/dev/button")
            with lock:
                print("SwitchShort Resetting")
                os.system("/opt/avnet-iot/iotservices/switch_reset")
    except Exception as ex:
        print("Reset Button Exception:" + str(ex))

def check_switch_long(lock):
    try:
        while 1:
            cat("/dev/reset")
            with lock:
                print("LongPress Resetting to Configuration State")
                os.system("/opt/avnet-iot/iotservices/switch_configuration_mode")
    except Exception as ex:
        print("Ap Mode Button Exception:" + str(ex))

def check_switch_factory(lock):
    try:
        while 1:
            cat("/dev/factoryreset")
            with lock:
                print("WARNING!!! LongPress Resetting to Factory State WARNING!!!")
                os.system("/opt/avnet-iot/iotservices/switch_factory_reset")
    except Exception as ex:
        print("Factory Button Exception:" + str(ex))

if __name__ == '__main__':
    print("Starting button service")
    print(os.path.exists('/dev/button'))

    SwitchLock = threading.Lock()
    threading.Thread(target=check_switch_long, args=(SwitchLock,)).start()
    threading.Thread(target=check_switch_short, args=(SwitchLock,)).start()
    threading.Thread(target=check_switch_factory, args=(SwitchLock,)).start()
    while 1:
        sleep(60*60)
