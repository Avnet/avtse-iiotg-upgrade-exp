import importlib
import sys
import os.path
import os
from iotconnect import IoTConnectSDK
import json
import time
import socket
import configparser
import wget
import ctypes
import threading
import traceback
import psutil
import re
import subprocess
from subprocess import PIPE, Popen
from collections import defaultdict
from datetime import datetime
import pyudev

global ThreadsRunningLast
global MessageCount
global myprint
global template_name
global isedge
global isgateway
global AUTH_BASEURL
global TEMPLATE_BASEURL
global DEVICE_BASEURL
global OnBoard
global ACCESS_TOKEN
global AccessOK
global uniqueId
global EndorsementKey
global serial_number
global template
global templateDescription
global deviceTemplateGuid
global cpId
global my_config_parser_dict
global my_sensor_dict
global my_rules_dict
global my_command_dict
global IoTConnectConnecting
global ThreadCount
global sdk
global ModbusDataLock
global ModbusSerialPort
global MinimalModbusSerialPort
MinimalModbusSerialPort = []
ModbusSerialPort = []
ModbusDataLock = threading.Lock()

ThreadsRunningLast = {}
#IoTConnectConnecting = 1
MessageCount = 0
template_name = 0
isedge = 0
isgateway = 0
AUTH_BASEURL = ""
TEMPLATE_BASEURL= ""
DEVICE_BASEURL= ""
ACCESS_TOKEN = None
serial_number = 0
EndorsementKey = "1" 
uniqueId = 0
template = 0
templateDescription = 0
deviceTemplateGuid = 0
cpId = None
my_config_parser_dict = {}
my_sensor_dict = defaultdict(dict)
my_rules_dict = defaultdict(dict)
my_command_dict = {}
ThreadCount = 0
d2cMsg = None
def mystr(input,format):
    if (sys.version_info[0] < 3):
        return str(input)
    else:
        return str(input,format)
    
def cmdline(command):
    process = Popen(
        args=command,
        stdout=PIPE,
        shell=True
    )
    return process.communicate()[0]

def ctype_async_raise(thread_obj, exception):
    found = False
    target_tid = 0
    for tid, tobj in threading._active.items():
        if tobj is thread_obj:
            found = True
            target_tid = tid
            break

    if not found:
        return

    ret = ctypes.pythonapi.PyThreadState_SetAsyncExc(target_tid, ctypes.py_object(exception))
    # ref: http://docs.python.org/c-api/init.html#PyThreadState_SetAsyncExc
    if ret == 0:
        raise ValueError("Invalid thread ID")
    elif ret > 1:
        # Huh? Why would we notify more than one threads?
        # Because we punch a hole into C level interpreter.
        # So it is better to clean up the mess.
        ctypes.pythonapi.PyThreadState_SetAsyncExc(target_tid, NULL)
        raise SystemError("PyThreadState_SetAsyncExc failed")
    #print "Successfully set asynchronized exception for", target_tid)
    

  
def DoCommand(msg):
    global my_command_dict
    global my_sensor_dict
    global my_config_parser_dict
    myprint("Executing command")
    command = str(msg['data']['command']).strip()
    data = command.split()
    if (data[0] == 'OmegaCommand'):
        myprint("Omega Cmd")
        output = data[1]
        for item in my_sensor_dict:
            if (str(item) == str(output)):
                myprint("\nFound Omega Output item")
                mydev = my_sensor_dict[item]['OmegaDev']
                mydev.Output_Data(int(my_sensor_dict[item]['OmegaSensorNumber']) - 1, int(data[2]), my_sensor_dict[item]['OmegaSSDevice']) 
                myprint("\nOmega Command executed on output " + str(item))
    else:    
        myprint("Python command " + str(command))
        globals()[my_command_dict[str(command)]](msg)
        for item in my_config_parser_dict:
            if 'name' in my_config_parser_dict[item].keys():
                if (my_config_parser_dict[item]['name'] == str(command)):
                    if (int(my_config_parser_dict[item]['requiresack']) == 1):
                        sendack = 1
                    else:
                        sendack = 0
        if (sendack == 1):
            header = {
                "ackId":msg['data']['ackId'],
                "st":7,
                "msg":"OK"
            }
            sdk.SendACK(header,5)

def myprint(arg):
    print(arg)
    sys.stdout.flush()
    sys.stderr.flush()

def DoOTACommand(msg):
    global sdk
    mystring=str(msg['data']['command'])
    if [ mystring.split(" ")[0] == "ota" ]:
        
        filename = wget.download(msg['data']['urls'][0]['url'])
        cmd = "mv " + filename + " install.gz "      
        os.system(cmd)
        cmd = "gunzip -c install.gz >install"
        os.system(cmd)
        cmd = "tar xf install"
        os.system(cmd)
        os.system("chmod 777 updates/install.sh")
        os.system("./updates/install.sh")
        header = {
            "ackId":msg['data']['ackId'],
            "st":7,
            "msg":"OK"
        } 
        myprint("Sending OTA Ack")
        sdk.SendACK(header,11)
      
def callbackTwinMessage(msg):
    if msg:
        myprint(json.dumps(msg))
        for item in OnBoard.callbackTwinChain:
            item(msg)

def callbackMessageThread(msg):
    try:
        
        global sdk, my_command_dict, d2cMsg
        myprint(msg)
        myprint(str(msg['data']['ack']))
        myprint(str(msg['data']['ackId']))
        myprint(str(msg['data']['command']))
        myprint(str(msg['data']['uniqueId']))
        if msg != None and len(list(msg.items())) != 0:
            cmdType = msg["cmdType"]
            data = msg["data"]
            # For Commands
            if cmdType == "0x01" and data != None:
                DoCommand(msg)
            # For OTA updates
            if cmdType == "0x02" and data != None:
                DoOTACommand(msg)
#        for item in OnBoard.callbackChain:
#            item(msg)
    except Exception as ex:
        exc_type, exc_value, exc_traceback = sys.exc_info()
        traceback.print_tb(exc_traceback)
        myprint(ex)
        sys.stdout.flush()
        sys.stderr.flush()

def callbackMessage(msg):
    x = threading.Thread(target=callbackMessageThread, args=(msg,))
    x.daemon = True
    x.start()
        
def ProcessRules(name):
    global my_rules_dict
    global my_sensor_dict
    try:
        for rulename in my_rules_dict:
            for sensorname in my_sensor_dict:
                if (my_sensor_dict[sensorname]["name"] == name):
                    break
                if( name == my_rules_dict[rulename]["sensor"]):
                    condition = str(my_rules_dict[rulename]["condition"])
                    conditionvalue = int(my_rules_dict[rulename]["conditionvalue"])
                    if (condition == "IsEqualTo"):
                        if (my_sensor_dict[sensorname]["value"] == conditionvalue):
                            globals()[my_rules_dict[rulename]["command"]]()
                    elif (condition == "IsNotEqualTo"):
                        if (my_sensor_dict[sensorname]["value"] != conditionvalue):
                            globals()[my_rules_dict[rulename]["command"]]()
                    elif (condition == "IsGreaterThan"):
                        if (my_sensor_dict[sensorname]["value"] > conditionvalue):
                            globals()[my_rules_dict[rulename]["command"]]()
                    elif (condition == "IsGreaterOrEqualTo"):
                        if (my_sensor_dict[sensorname]["value"] >= conditionvalue):
                            globals()[my_rules_dict[rulename]["command"]]()
                    elif (condition == "IsLessThan"):
                        if (my_sensor_dict[sensorname]["value"] < conditionvalue):
                            globals()[my_rules_dict[rulename]["command"]]()
                    elif (condition == "IsLessOrEqualTo"):
                        if (my_sensor_dict[sensorname]["value"] < conditionvalue):
                            globals()[my_rules_dict[rulename]["command"]]()
                    else:
                        myprint("Unknown Condition" + condition)
    except Exception as ex:
        myprint(ex.message)
    except KeyboardInterrupt:
        myprint(ex.message)

def ProcessSensorTask(name):
    global my_sensor_dict
    global sdk
    global uniqueId
    global OnBoard
    try:
        myprint("SensorTask "+ str(my_sensor_dict[name]["name"]))
        reportpolltime = my_sensor_dict[name]["reportpolltime"]
        lastvalue = globals()[my_sensor_dict[name]["usepythoninterface"]]()
        my_sensor_dict[name]["value"] = lastvalue
        while 1:
            value = globals()[my_sensor_dict[name]["usepythoninterface"]]()
            if (value == None):
                myprint("Error reading value, exiting task " + str(name))
                sys.exit(1)
            else:
                my_sensor_dict[name]["value"] = value

                lastvalue = OnBoard.QueueSensorValue(name, my_config_parser_dict[name], value,lastvalue)
            ProcessRules(my_sensor_dict[name]["name"])
            time.sleep(float(reportpolltime)) 
    except Exception as ex:
        exc_type, exc_value, exc_traceback = sys.exc_info()
        traceback.print_tb(exc_traceback)
        myprint(ex)
        sys.stdout.flush()
        sys.stderr.flush()

    



def main(argv):
    global my_config_parser_dict
    global cpId 
    global uniqueId
    global EndorsementKey
    global serial_number
    global my_sensor_dict
    global my_command_dict
    global sdk
    global ThreadCount
    global OnBoard
    global AccessOK
    global IoTConnectConnecting
    try:

        os.system('sudo chmod 666 /sys/class/leds/green/brightness')
        os.system('sudo chmod 666 /sys/class/leds/red/brightness')
        os.system('echo 0 >/sys/class/leds/red/brightness')
        os.system('echo 0 >/sys/class/leds/green/brightness')

        config = configparser.ConfigParser()
        config.read('IoTConnectSDK.conf.default')
        my_config_parser_dict = {s:dict(config.items(s)) for s in config.sections()}
        config.read('IoTConnectSDK.conf')
        my_config_parser_current_dict = {s:dict(config.items(s)) for s in config.sections()}
        my_config_parser_dict.update(my_config_parser_current_dict)        
        IoTConnectConnecting = 1
        if (int(my_config_parser_dict["CloudSystemControl"]["authtype"]) == 4):
            id_ek = cmdline("yes|/opt/avnet-iot/iotservices/tpm_device_provision")
            if(str.find(str(id_ek),"Error") != -1):
                id_ek = cmdline("yes|/opt/avnet-iot/iotservices/tpm_device_provision")
                if(str.find(id_ek,"Error") != -1):
                    print("Can't read TPM resetting")
                    os.system('reboot')
            lines = id_ek.splitlines()
            uniqueId = mystr(lines[3], 'utf-8')
            EndorsementKey = mystr(lines[6], 'utf-8')       
            myprint("EK")
            myprint(EndorsementKey)
        serialnumber = cmdline("tail /proc/cpuinfo")
        serialn = serialnumber.splitlines()
        serialn1 = serialn[9]
        serial_number = mystr(serialn1[-8:],'utf-8') 
        myprint(serial_number)
        OnBoard = __import__("IoTConnectSDKonboard")
        OnBoard.__init__(OnBoard,globals())
        globals().update(OnBoard.__dict__) 
        print("AccessToken")
        AccessOK = OnBoard.GetAccessToken()
        if (int(my_config_parser_dict["CloudSystemControl"]["systemconfigured"]) == 0):
            # Setup factory defaults
        
            configs = cmdline("find . -name IoTConnectSDK.conf")
            myprint(configs)
            configs = configs.splitlines()
            for item in configs:
                config = configparser.ConfigParser()
                item = item[2:len(item)]
                myprint(item)
                if (item.find(str("Plugin").encode(encoding='UTF-8')) != -1):
                    config.read(mystr(item,'utf-8'))
                    print("Importing PluginCfg " + mystr(item,'utf-8'))
                    my_config_parser_plugin_dict = {s:dict(config.items(s)) for s in config.sections()}
                    my_config_parser_dict.update(my_config_parser_plugin_dict)

        plugins = cmdline("find . -name 'IoTFnPlugin*'")
        plugins = plugins.splitlines()
        for item in plugins:
            item = item[2:len(item)]
            print("Importing FnPlugin " + mystr(item,'utf-8'))
            m = __import__(mystr(item,'utf-8'))
            m.__init__(m,globals())
            globals().update(m.__dict__)
        plugins = cmdline("find . -name 'IoTPlugin*'")
        plugins = plugins.splitlines()
        for item in plugins:
            item = item[2:len(item)]
            print("Importing Plugin " + mystr(item,'utf-8'))
            m = __import__(mystr(item, 'utf-8'))
            m.__init__(m,globals())
            globals().update(m.__dict__)
            
        #myprint(my_config_parser_dict)
        #print("Globals: " + str(globals()))
       
        scopeId = my_config_parser_dict["CloudSDKConfiguration"]["scopeid"]
        env = my_config_parser_dict["CloudSDKConfiguration"]["env"]
        cpId = my_config_parser_dict["CloudSDKConfiguration"]["cpid"]
        myprint(scopeId)
        myprint(env)
        myprint(cpId)
        if (int(my_config_parser_dict["CloudSystemControl"]["enabledebug"]) == 0):
            myprint("SDT output")
        else:
            myprint("Logging")
            sys.stdout = open(my_config_parser_dict["CloudSystemControl"]["debuglogfile"], 'a')
            sys.stderr = open(my_config_parser_dict["CloudSystemControl"]["debuglogfile"], 'a')
        #
        # Setup adjust cloud attributes/commands/rules
        #
        print("setup objects")
        if ((AccessOK == 1) ):
            OnBoard.CloudSetupObjects()
            time.sleep(float(5))
            OnBoard.CloudSetupFirmware()
            #my_config_parser_dict["CloudSystemControl"]["systemconfigured"] = 2
            # save value in config file
            config = configparser.ConfigParser()
            config.read('/opt/avnet-iot/IoTConnect/sample/IoTConnectSDK.conf')
            #config.set('CloudSystemControl', 'systemconfigured', '2')
        with open('/opt/avnet-iot/IoTConnect/sample/IoTConnectSDK.conf', 'w') as configfile:
            config.write(configfile)
            
        while 1:
        #
            with IoTConnectSDK(str(cpId), str(uniqueId), str(scopeId), callbackMessage, callbackTwinMessage, str(env)) as sdk:
                if (sdk == None):
                    myprint("No Nework Connection")
                    time.sleep(60)
                    continue
                OnBoard.Start(sdk)
                myprint("SDK Started")
                os.system('sudo touch /tmp/iotconnect.txt')
                ThreadCount = 0
                IoTConnectConnecting = 0
                attributes = sdk.GetAttributes()
                ThreadCount = ThreadCount + 1
                input = 'y'
                while input == 'y':
#                    count = int(my_config_parser_dict["CloudSystemControl"]["defaultobjectcount"])
                    for item in my_config_parser_dict:
                        if (str(item).find("Object") != -1):
                            x = threading.Thread(target=ProcessSensorTask, args=(str(item), ))
                            x.start()
                    while 1:
                       time.sleep(60)
    except Exception as ex:
        exc_type, exc_value, exc_traceback = sys.exc_info()
        traceback.print_tb(exc_traceback)
        myprint(ex)
        sys.stdout.flush()
        sys.stderr.flush()
        myprint("Exiting in 60 seconds" + str(ex))
    if (int(my_config_parser_dict["CloudSystemControl"]["useiotwatchdog"]) == 1):
        cmdline('/opt/avnet-iot/iotservices/stopwd')
    time.sleep(60)
    myprint("Quitting")           
    os.system('sudo rm /tmp/iotconnect.txt')
if __name__ == "__main__":
    main(sys.argv)
