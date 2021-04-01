import os
global ClearDigitalOutput3Now
global DigitalOutClear3Port

# SDK call backs
def callbackMessageDigitalOutClear3(msg):
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

def callbackTwinMessageDigitalOutClear3(msg):
    if msg:
        # Put code here to act on twin message
        myprint(json.dumps(msg))

def __init__(self,myglobals):
    globals().update(myglobals)
    OnBoard.RegisterCallbackMsg(callbackMessageDigitalOutClear3)
    OnBoard.RegisterCallbackTwinMsg(callbackTwinMessageDigitalOutClear3)
    DigitalOutClear3Port = int(my_config_parser_dict["IoTPluginDigitalOutputClear3Command1"]["usegpiooutput"])
    if (DigitalOutClear3Port == 1):        
        if os.path.isdir("/sys/class/gpio/gpio201"):
            dummy = 1 
        else:
            os.system("echo 201 >/sys/class/gpio/export")
            os.system("echo out >/sys/class/gpio/gpio201/direction")
    elif (DigitalOutClear3Port == 2):        
        if os.path.isdir("/sys/class/gpio/gpio203"):
            dummy = 1 
        else:
            os.system("echo 203 >/sys/class/gpio/export")
            os.system("echo out >/sys/class/gpio/gpio203/direction")
    elif (DigitalOutClear3Port == 3):        
        if os.path.isdir("/sys/class/gpio/gpio205"):
            dummy = 1 
        else:
            os.system("echo 205 >/sys/class/gpio/export")
            os.system("echo out >/sys/class/gpio/gpio205/direction")
    elif (DigitalOutClear3Port == 4):        
        if os.path.isdir("/sys/class/gpio/gpio207"):
            dummy = 1 
        else:
            os.system("echo 207 >/sys/class/gpio/export")
            os.system("echo out >/sys/class/gpio/gpio207/direction")
    else:
        print("Invalid port selected " + str(my_config_parser_dict["IoTPluginDigitalOutputClear3Command1"]["usegpiooutput"]))
    

#
# Predefined functions for commands.
#

def ClearDigitalOutput3Now(args):
    DigitalOutClear3Port = int(my_config_parser_dict["IoTPluginDigitalOutputClear3Command1"]["usegpiooutput"])
    if (DigitalOutClear3Port == 1):        
        os.system("echo 0 >/sys/class/gpio/gpio201/value")
    elif (DigitalOutClear3Port == 2):        
        os.system("echo 0 >/sys/class/gpio/gpio203/value")
    elif (DigitalOutClear3Port == 3):        
        os.system("echo 0 >/sys/class/gpio/gpio205/value")
    elif (DigitalOutClear3Port == 4):        
        os.system("echo 0 >/sys/class/gpio/gpio207/value")
    else:
        print("Invalid port selected " + str(my_config_parser_dict["IoTPluginDigitalOutputClear3Command1"]["usegpiooutput"]))
 
