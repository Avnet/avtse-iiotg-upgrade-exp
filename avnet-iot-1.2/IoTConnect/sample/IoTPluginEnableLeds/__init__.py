import os
global EnableLED

# SDK call backs
def callbackMessageEnableLeds(msg):
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

def callbackTwinMessageEnableLeds(msg):
    if msg:
        # Put code here to act on twin message
        myprint(json.dumps(msg))

def __init__(self,myglobals):
    globals().update(myglobals)
    OnBoard.RegisterCallbackMsg(callbackMessageEnableLeds)
    OnBoard.RegisterCallbackTwinMsg(callbackTwinMessageEnableLeds)
    

#
# Predefined functions for commands.
#
def EnableLED(args):
    os.system("sudo systemctl enable ledservice")
    os.system("sudo systemctl start ledservice")

