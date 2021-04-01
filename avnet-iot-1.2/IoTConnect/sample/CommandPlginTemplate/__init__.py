
global MyPythonCommand

# SDK call backs
def callbackMessageMyPythonCommand(msg):
    global sdk, my_command_dict, d2cMsg
    myprint(msg)
    myprint(str(msg['data']['ack']))
    myprint(str(msg['data']['ackId']))
    myprint(str(msg['data']['command']))
    myprint(str(msg['data']['uniqueId']))
    if msg != None and len(list(msg.items())) != 0:
        cmdType = msg["cmdType"]
        data = msg["data"]
        # For non OTA(commands etc)
        if cmdType != "0x02" and data != None:
            #
            # Put code here to do command
            #
            myprint("Message: " + str(msg))

def callbackTwinMessageMyPythonCommand(msg):
    if msg:
        # Put code here to act on twin message
        myprint(json.dumps(msg))

def __init__(self,myglobals):
    globals().update(myglobals)
    OnBoard.RegisterCallbackMsg(callbackMessageMyPythonCommand)
    OnBoard.RegisterCallbackTwinMsg(callbackTwinMessageMyPythonCommand)
    # Put code here to initialize hardware/software stacks

def MyPythonCommand():
    # Put code here that gets executed when the cloud command is received.
    myprint("Executing MyPythonCommand")
