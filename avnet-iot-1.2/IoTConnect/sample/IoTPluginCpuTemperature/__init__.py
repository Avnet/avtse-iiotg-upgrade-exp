global GetTheTemp

# SDK call backs
def callbackMessageCpuTemperature(msg):
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

def callbackTwinMessageCpuTemperature(msg):
    if msg:
        # Put code here to act on twin message
        myprint(json.dumps(msg))

def __init__(self,myglobals):
    globals().update(myglobals)
    OnBoard.RegisterCallbackMsg(callbackMessageCpuTemperature)
    OnBoard.RegisterCallbackTwinMsg(callbackTwinMessageCpuTemperature)

def GetTheTemp():
    global my_sensor_dict
    file_handle = open('/sys/class/thermal/thermal_zone0/temp', 'r')
    line = file_handle.readline()
    CpuTemperature =  float(float(line)/float(1000))
    file_handle.close()
    #for section in my_sensor_dict:
    #    if section[name] == 'CpuTemperature':
    #        CpuTemperature = round(CpuTemperature, section[name]["precision"])
    return CpuTemperature
