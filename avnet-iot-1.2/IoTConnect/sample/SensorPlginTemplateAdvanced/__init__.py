

def ProcessMyPythonSensorTask(name):
    global my_sensor_dict
    global uniqueId
    global sdk
    global OnBoard
    try:
        myprint("MyPythonSensorTask "+ name)
        #while(sdk == 0):
        time.sleep(float(20))
        time.sleep(2)
        reportpolltime = my_sensor_dict[name]["reportpolltime"]
        lastvalue = 0
        my_sensor_dict[name]["value"] = lastvalue
        while 1:
            time.sleep(float(reportpolltime)) 
            myprint("MyPythonSensorTask "+ name)
            value = globals()[my_sensor_dict[name]["usepythoninterface"]](name)
            lastvalue = OnBoard.QueueSensorValue(name, my_config_parser_dict["IoTPluginMySensorObject1"], value, lastvalue)
            
    except Exception as ex:
        myprint(ex.message)
        myprint("MyPythonSensor ExitTask")
    except KeyboardInterrupt as ex:
        myprint(ex.message)
        myprint("MyPythonSensor ExittaskKbd")
    except SystemExit as ex:
        myprint("MyPythonSensor SystemExit")
#
# Command functions 
#
def MyPythonSetOutput(msg):
    # put code here to do output
    myprint("MyPythonSetOutput")

# SDK call backs
def callbackMessageMyPythonAdv(msg):
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

def callbackTwinMessageMyPythonAdv(msg):
    if msg:
        # Put code here to act on twin message
        myprint(json.dumps(msg))

    OnBoard.RegisterCallbackMsg(callbackMessageMyPythonAdv)
    OnBoard.RegisterCallbackTwinMsg(callbackTwinMessageMyPythonAdv)

#
# Main initialization
#
def __init__(self,myglobals):
    globals().update(myglobals)
    global my_sensor_dict
    global my_config_parser_dict

    OnBoard.RegisterCallbackMsg(callbackMessage)
    OnBoard.RegisterCallbackTwinMsg(callbackTwinMessage)
    
    # Put your path here.  For use with custom imports
    sys.path.append(os.getcwd() + "/SensorPlginTemplateAdvanced")
    # Put code here to initialize hardware/software stacks

    # Retrieve current cloud setups
    commands = {}
    commands = OnBoard.GetCommands()
    attributes = {}
    attributes = OnBoard.GetAttributes()
    print("Commands: \n", + str(commands))
    print("Attributes: \n" + str(attributes))
    
    # Sensor attached and data collected now add attribute to cloud
    # This information is retrievied automatically from the IoTConnectSDK.conf file
    
    OnBoard.AddAttribute(my_config_parser_dict["IoTPluginMySensorObject1"])
    my_sensor_dict[name]["precision"] = int(my_config_parser_dict["precision"])    
    my_sensor_dict[name]["report"] = my_config_parser_dict["IoTPluginMySensorObject1"]["report"]
    my_sensor_dict[name]["reportpolltime"] = my_config_parser_dict["IoTPluginMySensorObject1"]["reportpolltime"]
    my_sensor_dict[name]["reportheartbeatcount"] = int(my_config_parser_dict["IoTPluginMySensorObject1"]["reportheartbeatcount"])
    my_sensor_dict[name]["heartbeatreload"] = int(my_config_parser_dict["IoTPluginMySensorObject1"]["reportheartbeatcount"])
    my_sensor_dict[name]["usepythoninterface"] = my_config_parser_dict["IoTPluginMySensorObject1"]["usepythoninterface"]

    my_sensor_dict[name]["pushdataalways"] = int(my_config_parser_dict["IoTPluginMySensorObject1"]["pushdataalways"])
    my_sensor_dict[name]["name"] = name
    ThreadCount = ThreadCount + 1
    x = threading.Thread(target=ProcessMyPythonSensorTask, args=(name,))
    x.start()
    my_sensor_dict[name]["OmegaSensorTask"] = x
    print("NameCreated: " + str(name))

    # Now an example of adding attributes not specified in IoTConnectSDK.conf
    # First build a local config_dict. Then call AddAttribute.
    # After adding then fill out critical my_sensor_dict variables
    name = "SelfGeneratedAttribute"
    config_dict = {}
    config_dict['name'] = name
    config_dict['description'] = description
    config_dict['units'] = units
    config_dict['value'] = "NUMBER"
    # For edge configured gateways
    config_dict['edgeaggregatetype'] = str(my_config_parser_dict["OmegaSensorConfiguration"]["edgeaggregatetype"])
    config_dict['edgetumblingwindow'] = str(my_config_parser_dict["OmegaSensorConfiguration"]["edgetumblingwindow"])
    response = OnBoard.AddAttribute(config_dict)
    #
    # response will contain guid if you want to save it for later
    #
    # Now fill in my_sensor_dict with IoTConnectSDK.conf parameters.
    #
    my_sensor_dict[name]["precision"] = int(my_config_parser_dict["precision"])    
    my_sensor_dict[name]["report"] = my_config_parser_dict["IoTPluginMySensorObject1"]["report"]
    my_sensor_dict[name]["reportpolltime"] = my_config_parser_dict["IoTPluginMySensorObject1"]["reportpolltime"]
    my_sensor_dict[name]["reportheartbeatcount"] = int(my_config_parser_dict["IoTPluginMySensorObject1"]["reportheartbeatcount"])
    my_sensor_dict[name]["heartbeatreload"] = int(my_config_parser_dict["IoTPluginMySensorObject1"]["reportheartbeatcount"])
    my_sensor_dict[name]["usepythoninterface"] = my_config_parser_dict["IoTPluginMySensorObject1"]["usepythoninterface"]

    my_sensor_dict[name]["pushdataalways"] = int(my_config_parser_dict["IoTPluginMySensorObject1"]["pushdataalways"])
    my_sensor_dict[name]["name"] = name
    

    # Now an example of adding commands not specified in IoTConnectSDK.conf
    # Build config_dict, then call AddCommand.
    # Fill out critical my_command_dict variables
    name = "SelfGeneratedCommand"
    config_dict = {}
    config_dict['commandname'] = str(name)
    config_dict['command'] = str(name)
    config_dict['hasparameter'] = 0
    config_dict['requiresack'] = 0
    config_dict['isiotcommand'] = 0
    config_dict['cmdText'] = str(name)
    response = OnBoard.AddCommand(config_dict)
    #
    # response will contain guid if you want to save it for later
    #
    # Now fill in my_command_dict with IoTConnectSDK.conf parameters.
    #
    if response != None and response["data"] != None:
        my_command_dict[name]["command"] = "MyPythonSetOutput"
    else:
        myprint("Couldn't add command " + str(name))
    
    # Now an example of adding rules not specified in IoTConnectSDK.conf
    # Build config_dict then call AddRule
    # Fill out critical my_rules_dict variables
    config_dict = {}
    config_dict['rulelocation'] = "Cloud"
    config_dict['name'] = "MyPythonRule"
    config_dict['ruletype'] = 1 # Standard rule
    config_dict['severity'] = "Critical"
    config_dict['condition'] = "MySensorName > 40" # from .conf file
    config_dict['command'] = "MyPythonSetOutput" # command to execute on condition
    OnBoard.AddRule(config_dict)
    

    
    
def MyPythonSensorValue():
    # Put code here to get Sensor Value from hardware and return it
    print("Returning 100");
    return 100

