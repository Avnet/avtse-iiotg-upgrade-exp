import os
global GetDigitalInput2

# SDK call backs
def callbackMessageDigitalIn2(msg):
    global sdk, my_command_dict, d2cMsg
    if msg != None and len(list(msg.items())) != 0:
        cmdType = msg["cmdType"]
        data = msg["data"]
        # For non OTA(commands etc)
        if cmdType != "0x02" and data != None:
            #
            # Put code here to do command
            #
            myprint("Message: " + str(msg))

def callbackTwinMessageDigitalIn2(msg):
    if msg:
        # Put code here to act on twin message
        myprint(json.dumps(msg))

def __init__(self,myglobals):
    globals().update(myglobals)
    OnBoard.RegisterCallbackMsg(callbackMessageDigitalIn2)
    OnBoard.RegisterCallbackTwinMsg(callbackTwinMessageDigitalIn2)
    if os.path.isdir("/sys/class/gpio/gpio202"):
        dummy = 1 
    else:
        os.system("echo 202 >/sys/class/gpio/export")
    

#
# Predefined functions for commands.
#

def GetDigitalInput2():
    file = open('/sys/class/gpio/gpio202/value','r')
    value = file.readline()
    file.close()
    return int(value)


