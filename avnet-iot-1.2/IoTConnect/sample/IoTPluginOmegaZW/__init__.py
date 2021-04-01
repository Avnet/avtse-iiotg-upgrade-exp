
import threading
import re
import ZW_REC_Interface
import sys
import os.path
import os
import json
import time
import socket
import ctypes
import re
from datetime import datetime
global OnBoard
global AccessOK

OmegaZWLock = threading.Lock()
ActiveIP = {}
# SDK call backs
def callbackMessageOmegaZW(msg):
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

def callbackTwinMessageOmegaZW(msg):
    if msg:
        # Put code here to act on twin message
        myprint(json.dumps(msg))
      
def __init__(self,myglobals):
    globals().update(myglobals)
    global OnBoard
    global AccessOK
    global my_config_parser_dict
    myprint("Starting Omega ZWRec Tasks")
    sys.path.append(os.getcwd() + "/IoTPluginOmegaZW")
    OnBoard.RegisterCallbackMsg(callbackMessageOmegaZW)
    OnBoard.RegisterCallbackTwinMsg(callbackTwinMessageOmegaZW)
    #
    # Start scanning for custom Omega ZW-REC devices.
    #
    if ((str(my_config_parser_dict["OmegaSensorZWConfiguration"]["zwrecconnectstatic"]) == str("Yes")) or (str(my_config_parser_dict["OmegaSensorZWConfiguration"]["zwrecconnectdynamic"]) == str("Yes"))):
        if (AccessOK == 1):
            y = threading.Thread(target=OmegaZWRecScan)
            y.start()
        else:
            myprint("Please add username/password to IoTConnectSDK.conf for Omega Plug&Play")
   
def ProcessOmegaZWSensorTask(name):
    myprint("Processing Omega ZW " + str(name))
    global my_sensor_dict
    global uniqueId
    global sdk
    global SendDataArray
    global SendDataLock
    global OmegaZWLock
    global PushDataNow
    global PushDataArray
    global my_config_parser_dict
    
    zw = my_sensor_dict[name]["zwsocket"]
    try:
        while(sdk == 0):
            time.sleep(float(10))
        time.sleep(2)
        report = my_sensor_dict[name]["report"]
        reportpolltime = my_sensor_dict[name]["reportpolltime"]
        lastvalue = 0
        value = -1
        pushdataalways = int(my_sensor_dict[name]["pushdataalways"])
        my_sensor_dict[name]["value"] = lastvalue
        while 1:
            zwip = my_sensor_dict[name]["OmegaDev"]
            zwip = str(zwip)
            zwip = zwip.strip('\r\n')
            if (OmegaCheckZWRec(zwip) == 0):
                myprint("Communications down ZWREC " + str(zwip))
                RemoveOmegaCloudAttribute(name)
                sys.exit(1) 
            else: 
                OmegaZWLock.acquire()
                value = zw.Sensor_Reading(my_sensor_dict[name]["OmegaSensorNumber"], my_sensor_dict[name]["OmegaDevice"])
                OmegaZWLock.release()
                if (value == None):
                    myprint("Error reading value exiting task " +str(name))
                    sys.exit(1)
                else:
                    my_sensor_dict[name]["value"] = value
                    lastvalue = OnBoard.QueueSensorValue(name, my_config_parser_dict["OmegaSensorZWConfiguration"], value, lastvalue)
             
            time.sleep(float(reportpolltime)) 
            
    except Exception as ex:
        exc_type, exc_value, exc_traceback = sys.exc_info()
        traceback.print_tb(exc_traceback)
        myprint(ex.message)
        myprint("Omega ZW-REC ExitTask")
    except KeyboardInterrupt as ex:
        exc_type, exc_value, exc_traceback = sys.exc_info()
        traceback.print_tb(exc_traceback)
        myprint(ex.message)
        myprint("Omege ZW-REC ExittaskKbd")
    except SystemExit as ex:
        exc_type, exc_value, exc_traceback = sys.exc_info()
        traceback.print_tb(exc_traceback)
        myprint("Omega ZW-REC SystemExit")

def OmegaCheckZWRec(zwip):
    zwrecip = cmdline("nmap -sn %s | grep 'scan report for' " % zwip)
    found = 0
    for line in zwrecip.splitlines():
        lines = line.split()
        line = "echo " + "'" + lines[4] + "'" + " | cut -d '(' -f2 | cut -d ')' -f1"
        line = cmdline(line)
        found = 1
    if (found == 0):
        myprint("NotFound")
        return 0 
    return 1                             

def RemoveOmegaCloudAttribute(name):
    myprint("Removing Omega Attribute")
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

def NewOmegaZWRecAttributes(zw, line, num, deviceid):
    myprint("Add ZW Attributes " + str(num) + str(zw))
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
        return
    header = { 
        "Content-type": "application/json",
        "Accept": "*/*",
        "Authorization": ACCESS_TOKEN
    } 
    #---------------------------------------------------------------------
    # Get attribute data types
    datatype = None
    #response = service_call("GET", TEMPLATE_BASEURL + "/device-template/datatype", header)
    #if response != None and response["data"] != None and len(response["data"]) > 0:
    #     datatype = {}
    #     for d in response["data"]:
    #        datatype[d["name"]] = d["guid"]
    
    # get attributes first
    header = {
        "Content-type": "application/json",
        "Accept": "*/*",
        "Authorization": ACCESS_TOKEN
    }
    description = "\rOmega ZWREC Sensor"
    count = 0
    while(count < num):
        name = "ZW_"+str(line).strip('\r\n')+"_Device_" + str(deviceid) +"_Sensor_" + str(count) 
        name = name.replace('.', '_')
        config_dict = {}
        config_dict['name'] = name
        config_dict['description'] = description
        config_dict['units'] = str(my_config_parser_dict["OmegaSensorZWConfiguration"]["zwrecunits"])
        config_dict['value'] = "NUMBER"
        config_dict['edgeaggregatetype'] = str(my_config_parser_dict["OmegaSensorZWConfiguration"]["edgeaggregatetype"])
        config_dict['edgetumblingwindow'] = str(my_config_parser_dict["OmegaSensorZWConfiguration"]["edgetumblingwindow"])
        config_dict['gatewaytagged'] = str(my_config_parser_dict["OmegaSensorZWConfiguration"]["gatewaytagged"])
        config_dict['childname'] = str(my_config_parser_dict["OmegaSensorZWConfiguration"]["childname"])
        response = OnBoard.AddAttribute(config_dict)

        if response != None and response["data"] != None:
            myprint("Created " + str(name))
        else:
            myprint("Already Exists Attribute " + name)
            return
        my_sensor_dict[name]["report"] = my_config_parser_dict["OmegaSensorZWConfiguration"]["zwrecsensorreport"]
        my_sensor_dict[name]["reportpolltime"] = my_config_parser_dict["OmegaSensorZWConfiguration"]["zwrecsensorreportpolltime"]
            
        my_sensor_dict[name]["pushdataalways"] = 0
        my_sensor_dict[name]["usepythoninterface"] = "OmegaGetValue"
        my_sensor_dict[name]["OmegaDevice"] = deviceid 
        my_sensor_dict[name]["OmegaSensorNumber"] = count
        my_sensor_dict[name]["OmegaDev"] = line.strip('\r\n')
        my_sensor_dict[name]["OmegaOutput"] = 0
        my_sensor_dict[name]["name"] = name
        my_sensor_dict[name]["zwsocket"] = zw
        my_sensor_dict[name]["reportheartbeatcount"] = my_config_parser_dict["OmegaSensorZWConfiguration"]["zwrecsensorreportheartbeatcount"]
        my_sensor_dict[name]["precision"] = int(my_config_parser_dict["OmegaSensorZWConfiguration"]["precision"])
        ThreadCount = ThreadCount + 1
        x = threading.Thread(target=ProcessOmegaZWSensorTask, args=(name,))
        x.start()
        my_sensor_dict[name]["OmegaSensorTask"] = x
        count = count + 1
    
def OmegaNewZWRec(line):
    global ActiveIP
    global OmegaZWLock
    myprint("Line " + str(line))
    import ZW_REC_Interface as zw
     
    OmegaZWLock.acquire()
    zw.reconnect(line)
    OmegaZWLock.release()
    count = 1 
    while (count < 32):
        OmegaZWLock.acquire()
        zw.get_sensor_info(count)
        num = zw.Num_Sensors()
        OmegaZWLock.release()

        if (num != 0):
            NewOmegaZWRecAttributes(zw, line, num, count)
        count = count  + 1    
    
def OmegaZWRecScan():
    global ActiveIP
    # Check only eth0 and eth1 for now
    foundline = 0
    Rescan = 0
    ScanStatic = 0
    ScanDynamic = 0
    if (str(my_config_parser_dict["OmegaSensorZWConfiguration"]["zwrecconnectstatic"]) == str("Yes")):
        ScanStatic = 1
        myprint("StaticScanning")
    if (str(my_config_parser_dict["OmegaSensorZWConfiguration"]["zwrecconnectdynamic"]) == str("Yes")):
        myprint("ScanDynamic")
        ScanDynamic = 1
    if (ScanStatic == 0) and (ScanDynamic == 0):
        # no scanning is configured were done.
        sys.exit(0)
    time.sleep(10)
    while 1:
        try:
            if (Rescan == 0):
                if (ScanStatic == 1):
                    myprint("Static scanning now")
                    cmd = "nmap -sn 169.254.1.* | grep 'scan report for' "
                    zwrecip = cmdline(cmd.encode())
                    for line in zwrecip.splitlines():
                        lines = line.split()
                        line = "echo " + "'" + lines[4] + "'" + " | cut -d '(' -f2 | cut -d ')' -f1"
                        line = cmdline(line.encode())
                        foundline = str(lines[4])
                        found = 0
                        for item in ActiveIP:
                            if (item == line):
                                found = 1
                        if (found == 0):
                            OmegaNewZWRec(line)
                            ActiveIP[line] = line
                if (ScanDynamic == 1):
                    foundline = 0
                    is_eth0 = cmdline("ifconfig eth0 | grep inet")
                    if (is_eth0 != ""):
                        cmd = "ip -o -f inet addr show eth0| awk '/scope global/ {print $6}' | cut -d '(' -f2 | cut -d ')' -f1"
                        subnet = cmdline(cmd.encode())
                        subnet = subnet.decode().replace("255", "*")
                        subnet = subnet.strip()
                        if (subnet.find("169.254") == -1):
                            cmd = "nmap -sn " + subnet + "| grep zwrec"
                            zwrecip = cmdline(cmd.encode())
                            myprint(zwrecip)
                            for line in zwrecip.splitlines():
                                found = 0
                                thiszw = str(my_config_parser_dict["OmegaSensorZWConfiguration"]["zwrecconnectdynamicnames"])
                                if (thiszw != str("All")):
                                    for thisone in thiszw.split():
                                        if (line.find(thisone) != -1):
                                            found = 1
                                        else:
                                            myprint("NotFound " + str(thisone))
                                else:
                                    found = 1
                                if (found == 1):
                                    line = "echo " + "'" + line.strip() + "'" + " | cut -d '(' -f2 | cut -d ')' -f1"
                                    line = cmdline(line.encode())
                                    foundline = line
                                    found = 0
                                    for item in ActiveIP:
                                        if (item == line):
                                            found = 1
                                    if (found == 0):
                                        OmegaNewZWRec(line)
                                        ActiveIP[line] = line
                    is_eth1 = cmdline("ifconfig eth1 | grep inet")
                    if (is_eth1 != ""):
                        cmd = "ip -o -f inet addr show eth1| awk '/scope global/ {print $6}' | cut -d '(' -f2 | cut -d ')' -f1"
                        subnet = cmdline(cmd.encode())
                        subnet = subnet.decode().replace("255", "*")
                        subnet = subnet.strip()
                        if (subnet.find("169.254") == -1):
                            cmd = "nmap -sn " + subnet + "| grep zwrec"
                            zwrecip = cmdline(cmd.encode())
                            zwrecip = zwrecip.decode('utf-8')
                            for line in zwrecip.splitlines():
                                found = 0
                                thiszw = str(my_config_parser_dict["OmegaSensorZWConfiguration"]["zwrecconnectdynamicnames"])
                                if (thiszw != str("All")):
                                    for thisone in thiszw.split():
                                        if (line.find(thisone) != -1):
                                            found = 1
                                        else:
                                            myprint("NotFound " + str(thisone))
                                    else:
                                        found = 1
                                    if (found == 1):
                                        line = "echo " + "'" + line.strip() + "'" + " | cut -d '(' -f2 | cut -d ')' -f1"
                                        line = cmdline(line.encode())
                                        foundline = line
                                        for item in ActiveIP:
                                            if (item == line):
                                                found = 1
                                        if (found == 0):
                                            OmegaNewZWRec(line)
                                            ActiveIP[line] = line

            time.sleep(60)
        except Exception as ex:
            #myprint("ZW Scan exception")
            exc_type, exc_vluue, exc_traceback = sys.exc_info()
            traceback.print_tb(exc_traceback)
            myprint(ex)
            sys.stdout.flush()
            sys.stderr.flush()
            sys.exit(0)
     


    

            



                
