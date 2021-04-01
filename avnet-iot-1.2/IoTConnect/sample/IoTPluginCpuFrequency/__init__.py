import os
global GetTheFreq

# SDK call backs
def callbackMessageCpuFrequency(msg):
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

def callbackTwinMessageCpuFrequency(msg):
    if msg:
        # Put code here to act on twin message
        myprint(json.dumps(msg))

def __init__(self,myglobals):
    globals().update(myglobals)
    OnBoard.RegisterCallbackMsg(callbackMessageCpuFrequency)
    OnBoard.RegisterCallbackTwinMsg(callbackTwinMessageCpuFrequency)
   

#
# Predefined functions for commands.
#


def GetTheFreq():
    file_handle = open('/sys/devices/system/cpu/cpu0/cpufreq/scaling_cur_freq', 'r')
    line = file_handle.readline()
    CpuFrequency = int(line)/100000
    file_handle.close()
    return(CpuFrequency)



