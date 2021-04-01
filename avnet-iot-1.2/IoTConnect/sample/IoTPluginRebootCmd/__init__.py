import os
global RebootNow


def callbackTwinMessageReboot(msg):
    if msg:
        # Put code here to act on twin message
        myprint(json.dumps(msg))

def __init__(self,myglobals):
    globals().update(myglobals)
    OnBoard.RegisterCallbackTwinMsg(callbackTwinMessageReboot)
    

#
# Predefined functions for commands.
#


def RebootNow(msg):
    os.system("/sbin/reboot")

