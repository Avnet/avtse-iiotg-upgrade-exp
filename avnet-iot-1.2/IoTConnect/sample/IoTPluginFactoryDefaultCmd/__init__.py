import os
global FactoryDefaultNow

# SDK call backs

def callbackTwinMessageFactory(msg):
    if msg:
        # Put code here to act on twin message
        myprint(json.dumps(msg))

def __init__(self,myglobals):
    globals().update(myglobals)
    OnBoard.RegisterCallbackTwinMsg(callbackTwinMessageFactory)

#
# Predefined functions for commands.
#

def FactoryDefaultNow(msg):
    os.system("/opt/avnet-iot/iotservices/switch_only")
