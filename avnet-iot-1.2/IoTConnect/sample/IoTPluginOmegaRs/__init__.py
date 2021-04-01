
from collections import defaultdict
import threading
import sys
import os.path
import os
import json
import time
import minimalmodbus
import ctypes
from datetime import datetime
global OnBoard
global AccessOK
OmegaSSLock = threading.Lock()
Aquired_Usb = defaultdict(dict)     
ActiveIP = {}

def ProcessOmegaSensorRsTask(name):
    global my_sensor_dict
    global uniqueId
    global sdk
    global OnBoard
    
    try:
        myprint("OmegaSensorTask "+ name)
        #while(sdk == 0):
        time.sleep(float(20))
        time.sleep(2)
        report = my_sensor_dict[name]["report"]
        reportpolltime = my_sensor_dict[name]["reportpolltime"]
        pushdataalways = int(my_sensor_dict[name]["pushdataalways"])
        lastvalue = 0
        my_sensor_dict[name]["value"] = lastvalue
        while 1:
            time.sleep(float(reportpolltime)) 
            value = globals()[my_sensor_dict[name]["usepythoninterface"]](name)
            if (value == None):
                # special case (? May need string to detect
                myprint("Omega reading fault! " + str(name))
                mydev = my_sensor_dict[name]["OmegaDev"]
                mydev.debug = True
            else:
                my_sensor_dict[name]["value"] = value
                lastvalue = OnBoard.QueueSensorValue(name, my_config_parser_dict["OmegaSensorRsConfiguration"], value, lastvalue)
            
    except Exception as ex:
            myprint(ex.message)
            myprint("Omega ExitTask")
    except KeyboardInterrupt as ex:
            myprint(ex.message)
            myprint("Omega ExittaskKbd")
    except SystemExit as ex:
            myprint("Omega SystemExit")

    


    
def AddNewOmegaCloudAttribute(devname, mydev, count, Device):
    dev_id = mydev.Device_ID(Device)
    my_name = mydev.Sensor_Name(count-1,Device)
    device_name = mydev.Device_Type(Device)
    device_name = re.sub('[^0-9a-zA-Z^]+', '',device_name)
    name = str(my_name.rstrip('\0'))
    name = name.replace(' ', '')
    name = name.replace('_','')
    name = re.sub('[^0-9a-zA-Z^]+','',name)
    name = name[:31]

    global ACCESS_TOKEN,AUTH_BASEURL,TEMPLATE_BASEURL,DEVICE_BASEURL
    global my_config_parser_dict, my_sensor_dict, my_command_dict, my_rules_dict
    global uniqueId
    global isedge
    global isgateway
    global template
    global template_name
    global ThreadCount
    global templateDescription
    role = my_config_parser_dict["CloudSystemControl"]["role"]

    if template == None:
        myprint("Device template does not exist Configuring and Registering Device on Cloud!")
        return
    header = { 
        "Content-type": "application/json",
        "Accept": "*/*",
        "Authorization": ACCESS_TOKEN
    } 
    #---------------------------------------------------------------------
    # Get attribute data types
    datatype = None
    #print("TemplateBase: " + str(globals()['TEMPLATE_BASEURL']))
    #response = service_call("GET", TEMPLATE_BASEURL + "/device-template/datatype", header)
    #print("AddAttributeServiceCallAns")
    #if response != None and response["data"] != None and len(response["data"]) > 0:
    #    datatype = {}
    #    for d in response["data"]:
    #        datatype[d["name"]] = d["guid"]
    

    description = "\rOmega "
    description = description + "FW " + str(mydev.Firmware_Version(Device)) + " CV " + str(mydev.Core_Version(Device)) + " HW " + str(mydev.Hardware_Version(Device))
    description = description + "\rDate " + str(mydev.Manufactured_Date(Device))
    description = description + "\rCal " + str(mydev.Calibration_Date(Device))
    description = description + "\rMin " + str(mydev.Sensor_Min_Value(count - 1,Device)) + " Max " + str(mydev.Sensor_Max_Value(count - 1, Device)) + " RMin " + str(mydev.Sensor_Min_Range(count - 1,Device)) + "RMax " + str(mydev.Sensor_Max_Range(count - 1,Device))
    description = description + "\rPrecision " + str(mydev.Sensor_Precision(count - 1,Device)) + " Measure " + str(mydev.Sensor_Measurement(count - 1,Device)) + " Gain " + str(mydev.Sensor_Scale_Gain(count - 1,Device)) + " Offset " + str(mydev.Sensor_Scale_Offset(count - 1,Device))
    units = str(mydev.Sensor_Units(count -1, Device))
    units = re.sub('[^0-9a-zA-z^]+', '_',units)

    # make up structure for add attribute
    config_dict = {}
    config_dict['name'] = name
    config_dict['description'] = description
    config_dict['units'] = units
    config_dict['value'] = "NUMBER"
    config_dict['edgeaggregatetype'] = str(my_config_parser_dict["OmegaSensorRsConfiguration"]["edgeaggregatetype"])
    config_dict['edgetumblingwindow'] = str(my_config_parser_dict["OmegaSensorRsConfiguration"]["edgetumblingwindow"])
    config_dict['gatewaytagged'] = str(my_config_parser_dict["OmegaSensorRsConfiguration"]["gatewaytagged"])
    config_dict['childname'] = str(my_config_parser_dict["OmegaSensorRsConfiguration"]["childname"])
    attributes = {}
    response = OnBoard.GetAttributes()
    if response != None and response["data"] != None:
        attributes = response["data"]
    create = 0
    for attr in attributes:
        if (attr["localname"] == name):
            create = 1
            myprint("Already Exists Attribute " + name)          
            break
    if (create == 0):
        response = OnBoard.AddAttribute(config_dict)

        if response != None and response["data"] != None:
            myprint("Created " + str(name))
        else:
            myprint("Error Creating Attribute " + name)
    my_sensor_dict[name]["precision"] = int(mydev.Sensor_Precision(count - 1,Device))
    my_sensor_dict[name]["report"] = my_config_parser_dict["OmegaSensorRsConfiguration"]["report"]
    my_sensor_dict[name]["reportpolltime"] = my_config_parser_dict["OmegaSensorRsConfiguration"]["reportpolltime"]
    my_sensor_dict[name]["reportheartbeatcount"] = int(my_config_parser_dict["OmegaSensorRsConfiguration"]["reportheartbeatcount"])
    my_sensor_dict[name]["usepythoninterface"] = "OmegaGetValue"
    my_sensor_dict[name]["pushdataalways"] = 0
    my_sensor_dict[name]["OmegaDevice"] = name
    my_sensor_dict[name]["OmegaSensorNumber"] = count
    my_sensor_dict[name]["OmegaDev"] = mydev
    my_sensor_dict[name]["OmegaDevName"] = devname
    my_sensor_dict[name]["OmegaOutput"] = 0
    my_sensor_dict[name]["name"] = name
    my_sensor_dict[name]["OmegaSSDevice"] = Device
    ThreadCount = ThreadCount + 1
    x = threading.Thread(target=ProcessOmegaSensorRsTask, args=(name,))
    x.start()
    my_sensor_dict[name]["OmegaSensorTask"] = x

# SDK call backs
def callbackMessageOmegaRs(msg):
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

def callbackTwinMessageOmegaRs(msg):
    if msg:
        # Put code here to act on twin message
        myprint(json.dumps(msg))

def __init__(self,myglobals):
    globals().update(myglobals)
    global my_config_parser_dict
    global AccessOK
    OnBoard.RegisterCallbackMsg(callbackMessageOmegaRs)
    OnBoard.RegisterCallbackTwinMsg(callbackTwinMessageOmegaRs)
    sys.path.append(os.getcwd() + "/IoTPluginOmegaRs")
    myprint("Starting Omega Rs485 Tasks")
    if (str(my_config_parser_dict["OmegaSensorRsConfiguration"]["rs485modbus"]) == str("Yes")):
        if (AccessOK == 1):
            OmegaRsModbusScan()
        else:
            myprint("Please add username/password to IoTConnectSDK.conf for RS485 Plug&Play")


   

def RemoveOmegaCloudAttribute(name):
    global ACCESS_TOKEN,AUTH_BASEURL,TEMPLATE_BASEURL,DEVICE_BASEURL
    global my_config_parser_dict, my_sensor_dict, my_command_dict, my_rules_dict
    global uniqueId
    global template
    if template == None:
        return
    header = {
        "Content-type": "application/json",
        "Accept": "*/*",
        "Authorization": ACCESS_TOKEN
    }
    #---------------------------------------------------------------------
    # Get attribute data types
    #datatype = None
    #response = service_call("GET", TEMPLATE_BASEURL + "/device-template/datatype", header)
    #if response != None and response["data"] != None and len(response["data"]) > 0:
    #    datatype = {}
    #    for d in response["data"]:
    #        datatype[d["name"]] = d["guid"]
    
    # get attributes first
    header = {
        "Content-type": "application/json",
        "Accept": "*/*",
        "Authorization": ACCESS_TOKEN
    }
 
    if (isedge == 1):
        body = {
            "localName": name, 
            "deviceTemplateGuid": deviceTemplateGuid,
            "dataTypeGuid": datatype['NUMBER'],
            "tag": template_name
        }   
    else:
        body = {
            "localName": name, 
            "deviceTemplateGuid": deviceTemplateGuid,
            "dataTypeGuid": datatype['NUMBER']
        }   

    # get attributes first
    header = {
        "Content-type": "application/json",
        "Accept": "*/*",
        "Authorization": ACCESS_TOKEN
    }
    attributes = []
    response = GetAttributes()
    if response != None and response["data"] != None and len(response["data"]) > 0:
        attributes = response["data"]
    
    if len(attributes) > 0:
        for attr in attributes:
            attributeGuid = str(attr["guid"]) 
            if (str(attr["localname"]) == name):
                # delete this one.
                response = OnBoard.DeleteAttribute(attributeGuid)
                if response != None and response["data"] != None:
                    myprint("Deleted " + str(name))
                else:
                    myprint("Deleted None")

def OmegaRsModbusScan():
    global my_config_parser_dict
    os.system("sudo chmod 777 /dev/ttySC0")
    import Smart_Sensor as ss
    devname = str(my_config_parser_dict["OmegaSensorRsConfiguration"]["rs485modbusport"])
    slaves = my_config_parser_dict["OmegaSensorRsConfiguration"]["rs485modbusslaveaddresses"]
    OmegaSSLock.acquire()
    for item in slaves.split():
        try:
            myprint("Trying SlaveAddress " + str(item))
            mydev = ss.SmartSensor(devname, int(item))
            ss.Device.serial.baudrate = int(my_config_parser_dict["OmegaSensorRsConfiguration"]["rs485modbusbaud"])
            ss.Device.serial.parity = str(my_config_parser_dict["OmegaSensorRsConfiguration"]["rs485modbusparity"])
            ss.Device.serial.stopbits = int(my_config_parser_dict["OmegaSensorRsConfiguration"]["rs485modbusstopbits"])
            ss.Device.serial.databits = int(my_config_parser_dict["OmegaSensorRsConfiguration"]["rs485modbusdatabits"])
            sensor_count = mydev.Number_Of_Sensors(ss.Device)
            while (sensor_count !=0):
                AddNewOmegaCloudAttribute(devname, mydev,sensor_count,ss.Device)
                sensor_count = sensor_count - 1
            output_count = mydev.Number_Of_Outputs(ss.Device)
            while (output_count != 0):
                AddNewOmegaCloudCommand(devname, mydev, output_count,ss.Device)
                output_count = output_count - 1
        except:
            myprint("No Serial Communications to " + str(devname) + " SlaveAdress " + str(item))
        OmegaSSLock.release()
    
def OmegaGetValue(name):
    try:
        value = -1
        count = my_sensor_dict[name]["OmegaSensorNumber"]
        mydev = my_sensor_dict[name]["OmegaDev"]
        Device = my_sensor_dict[name]["OmegaSSDevice"]
        OmegaSSLock.acquire()
        value = mydev.Sensor_Reading(count - 1,Device)
        OmegaSSLock.release()
    except:
        myprint("Omega Exception")
        return 
    return round(value, my_sensor_dict[name]["precision"]) 
    

    
def AddNewOmegaCloudCommand(devname, mydev, count,Device):
    myprint("Adding Omega Command")

    dev_id = mydev.Device_ID(Device)
    my_name = mydev.Output_Name(count-1,Device)
    device_name = mydev.Device_Type(Device)
    device_name = device_name.replace('-', '_')
    name = str(my_name.rstrip('\0'))
    name = name.replace(' ', '_')
    myprint("Adding Omega Command")

    global ACCESS_TOKEN,AUTH_BASEURL,TEMPLATE_BASEURL,DEVICE_BASEURL
    global my_config_parser_dict, my_sensor_dict, my_command_dict, my_rules_dict
    global uniqueId
    global template
    global deviceTemplateGuid
    role = my_config_parser_dict["CloudSystemControl"]["role"]

    if template == None:
        myprint("No Omega template on cloud!!")
        return
    #---------------------------------------------------------------------
    

    config_dict = {}
    config_dict['commandname'] = str(name) + "Set"
    config_dict['command'] = "OmegCommand " + str(name) + " 100"
    config_dict['hasparameter'] = 0
    config_dict['requiresack'] = 0
    config_dict['isiotcommand'] = 0
    response = OnBoard.AddCommand(config_dict)
 
    if response != None and response["data"] != None:
        myprint("Omega command added")
    else:
        myprint("Couldnt add command " + str(name))

        #  ???? TODO CHECK ????"cmdText" : str(name) + "0",
    config_dict['commandname'] = str(name) + "Clear"
    config_dict['command'] = "OmegCommand " + str(name) + " 0"
    config_dict['hasparameter'] = 0
    config_dict['requiresack'] = 0
    config_dict['isiotcommand'] = 0
    response = OnBoard.AddCommand(config_dict)
    if response != None and response["data"] != None:
        my_sensor_dict[name]["OmegaDevice"] = name
        my_sensor_dict[name]["OmegaSensorNumber"] = count
        my_sensor_dict[name]["OmegaDev"] = mydev
        my_sensor_dict[name]["OmegaDevName"] = devname
        my_sensor_dict[name]["OmegaOutput"] = 1
        my_sensor_dict[name]["OmegaSSDevice"] = Device
        my_sensor_dict[name]["name"] = name
    else:
        myprint("Couldnt add command " + str(name))
       
def RemoveOmegaCloudCommand(name):
    global ACCESS_TOKEN,AUTH_BASEURL,TEMPLATE_BASEURL,DEVICE_BASEURL
    global my_config_parser_dict, my_sensor_dict, my_command_dict, my_rules_dict
    global uniqueId
    global template
    global deviceTemplateGuid
    if template == None:
        return
    cloud_commands = []
    response = GetCommands()
    if response != None and response["data"] != None and len(response["data"]) > 0:
        cloud_commands = response["data"]
    else:
        temp = 0
    if len(cloud_commands) > 0:
        for attr in cloud_commands:
            if (attr['name'].find(name) == 0):
                attributeGuid = str(attr["guid"])
                response = OnBoard.DeleteCommand(attributeGuid)
                if response != None and response["data"] != None:
                    myprint("Deleted " + str(name))
                else:
                    myprint("None")
    
def AddOmegaRules(devname):
    global my_sensor_dict
    global my_config_parser_dict
    global ACCESS_TOKEN
    global deviceTemplateGuid
    myprint("Adding Omega Rules")
    count = int(my_config_parser_dict["CloudSystemControl"]["defaultomegarulecount"])
    myprint("Omega rule count " + str(count))
    entityguid = my_config_parser_dict["CloudSystemControl"]["entity_guid"]
    entityguid = str(entityguid)
    #count = int(my_config_parser_dict["CloudSystemControl"]["defaultrulecount"])
    header = {
    "Content-type": "application/json",
        "Accept": "*/*",
        "Authorization": ACCESS_TOKEN
    }
    attributes = []
    #response = service_call("GET", str(my_config_parser_dict["CloudSystemControl"]["http_rule_template"])+"/Rule" , header)
    #if response != None and response["data"] != None and len(response["data"]) > 0:
    #    attributes = response["data"]
    #device_name = uniqueId
    #severity_levels = []
    #response = service_call("GET", str(my_config_parser_dict["CloudSystemControl"]["http_event_template"])+"/severity-level/lookup" , header)
    #if response != None and response["data"] != None and len(response["data"]) > 0:
    #    severity_levels = response["data"]

    #user_guid = 0  
    #cloud_users = []
    #response = service_call("GET", str(my_config_parser_dict["CloudSystemControl"]["http_user_template"])+"/user/lookup" , header)
    #if response != None and response["data"] != None and len(response["data"]) > 0:
    #    cloud_users = response["data"]
    #for item in cloud_users:
    #    if (item['userid'] == my_config_parser_dict["CloudSystemControl"]["username"]):
    #        user_guid = item['guid']

    #cloud_roles = []
    #response = service_call("GET", str(my_config_parser_dict["CloudSystemControl"]["http_user_template"])+"/role/lookup" , header)
    #if response != None and response["data"] != None and len(response["data"]) > 0:
    #    cloud_roles = response["data"]
    #role_guid = 0
    #for role in cloud_roles:
    #    if (role['name'] == my_config_parser_dict["CloudSystemControl"]["role"]):
    #        role_guid = role['guid']
    #cloud_devices = []
    #response = service_call("GET", str(my_config_parser_dict["CloudSystemControl"]["http_device_template"])+"/device/lookup" , header)
    #if response != None and response["data"] != None and len(response["data"]) > 0:
    #    cloud_devices = response["data"]
    #for item in cloud_devices:
    #    if(device_name == item['uniqueId']):
    #        device_guid = item['guid']
    cloud_commands = []
    response = GetCommands()
    if response != None and response["data"] != None and len(response["data"]) > 0:
        cloud_commands = response["data"]
    while (count != 0):
        location = my_config_parser_dict["CloudSDKCustomOmegaRule"+str(count)]["rulelocation"]
        if (location == "Local"):
            myprint("Setup Local Rule")
            my_rules_dict["CloudSDKCustomOmegaRule"+str(count)]["name"] = my_config_parser_dict["CloudSDKCustomOmegaRule"+str(count)]["name"]            
            my_rules_dict["CloudSDKCustomOmegaRule"+str(count)]["sensor"] = my_config_parser_dict["CloudSDKCustomOmegaRule"+str(count)]["sensor"]
            my_rules_dict["CloudSDKCustomOmegaRule"+str(count)]["command"] = my_config_parser_dict["CloudSDKCustomOmegaRule"+str(count)]["command"]
            my_rules_dict["CloudSDKCustomOmegaRule"+str(count)]["condition"] = my_config_parser_dict["CloudSDKCustomOmegaRule"+str(count)]["condition"]
            my_rules_dict["CloudSDKCustomOmegaRule"+str(count)]["conditionvalue"] = my_config_parser_dict["CloudSDKCustomOmegaRule"+str(count)]["conditionvalue"]
        elif (location == "Cloud"):
            myprint("Setup Cloud Rule")
            name = my_config_parser_dict["CloudSDKCustomOmegaRule"+str(count)]["name"]  
            create = 0
            myprint("Rule " + str(name))
            for attr in attributes:
                if (attr["name"] == name):
                    create = 1
                    myprint("Exists " + name);
                    break
            if (create == 0):
                myprint("Creating")
                severity_guid = 0
                cloud_command_guid = 0
                for item in cloud_commands:
                    if(item['name'] == my_config_parser_dict["CloudSDKCustomOmegaRule"+str(count)]["command"]):
                        cloud_command_guid = item['guid']
                for level in severity_levels:
                    if (level["SeverityLevel"] == my_config_parser_dict["CloudSDKCustomOmegaRule"+str(count)]["severity"]):severity_guid = level["guid"]
                body = {
                    "name": name, 
                    "templateGuid": deviceTemplateGuid,
                    "ruleType": "1", #my_config_parser_dict["CloudSDKCustomOmegaRule"+str(count)]["ruletype"],
                    "severityLevelGuid": severity_guid,
                    "conditionText": my_config_parser_dict["CloudSDKCustomOmegaRule"+str(count)]["condition"],
                    "ignorePreference": 0, 
                    "entityGuid":entityguid,
                    "applyTo":"1",
                    "devices":[device_guid],
                    "roles":[role_guid],
                    "users":[user_guid],
                    "deliveryMethod":["DeviceCommand"],
                    "commandGuid": cloud_command_guid,
                    "parameterValue": "",
                    "customETPlaceHolders": {}, 
                }   
                response = service_call("POST", str(my_config_parser_dict["CloudSystemControl"]["http_rule_template"] + "/Rule"), header, body)
                if response != None and response["data"] != None:
                    myprint("Created " + name)
                else:
                    myprint("Couldn't Create Rule " + name)            
        count = count - 1;
    myprint("Rules synced with Cloud")
        



                
