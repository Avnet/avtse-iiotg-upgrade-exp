global MyPythonSensorValue

# SDK call backs
def callbackMessageMyPythonSensorValue(msg):
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

def callbackTwinMessageMyPythonSensorValue(msg):
    if msg:
        # Put code here to act on twin message
        myprint(json.dumps(msg))

def __init__(self,myglobals):
    globals().update(myglobals)
    OnBoard.RegisterCallbackMsg(callbackMessageMyPythonSensorValue)
    OnBoard.RegisterCallbackTwinMsg(callbackTwinMessageMyPythonSensorValue)
    # Put code here to initialize hardware/software stacks

def MyPythonSensorValue():
    # Put code here to get Sensor Value from hardware and return it
    print("Returning 100");
    return 100

