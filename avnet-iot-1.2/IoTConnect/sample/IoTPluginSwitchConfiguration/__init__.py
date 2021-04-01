import os
global SwitchToConfiguration


def callbackTwinMessageSwitch(msg):
    if msg:
        # Put code here to act on twin message
        myprint(json.dumps(msg))

def __init__(self,myglobals):
    globals().update(myglobals)
    OnBoard.RegisterCallbackTwinMsg(callbackTwinMessageSwitch)
    

#
# Predefined functions for commands.
#

def SwitchToConfiguration(args):
    os.system("/opt/avnet-iot/iotservices/switch_only_configs")

