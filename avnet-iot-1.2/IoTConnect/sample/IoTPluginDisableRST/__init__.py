import os
global DisableRST

# SDK call backs
def callbackMessageDisableRST(msg):
    global sdk, my_command_dict, d2cMsg
    myprint(str(msg['data']['command']))
    if msg != None and len(list(msg.items())) != 0:
        cmdType = msg["cmdType"]
        data = msg["data"]
        # For non OTA(commands etc)
        if cmdType != "0x02" and data != None:
            #
            # Put code here to do command
            #
            myprint("Message: " + str(msg))

def callbackTwinMessageDisableRST(msg):
    if msg:
        # Put code here to act on twin message
        myprint(json.dumps(msg))

def __init__(self,myglobals):
    globals().update(myglobals)
    OnBoard.RegisterCallbackMsg(callbackMessageDisableRST)
    OnBoard.RegisterCallbackTwinMsg(callbackTwinMessageDisableRST)
    

#
# Predefined functions for commands.
#
def DisableRST(args):
    os.system("sudo systemctl disable buttonservice")
    os.system("sudo systemctl stop buttonservice")

