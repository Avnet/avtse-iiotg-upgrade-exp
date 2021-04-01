from io import BytesIO
import py_compile
import threading
import traceback
import sys
import os
import json
import re
import time
import configparser
import subprocess
from subprocess import PIPE, Popen
from collections import defaultdict
from datetime import datetime
global my_configs_dict
my_configs_dict = {}
component_selected_dict = {}
def cmdline(command):
    process = Popen(
        args=command,
        stdout=PIPE,
        shell=True
    )
    return process.communicate()[0]

def input_choice(option1, option2):
    val = -1
    while(val == -1):
        line = raw_input("\nEnter " + str(option1) + " or " +str(option2) + ": ")
        line = line.strip()
        line = str(line)
        val = option2.find(line)
        if (val == -1):
            if (line.isdigit() == False):
                print("Invalid choice\033[3A")
            else:
                val = 0
    return line

def check_configuration():
    
    global my_configs_dict
    use232 = 0
    use485 = 0
    ports232 = []
    ports485 = []
    gpios_in = []
    gpios_out = []
    for item in my_configs_dict:
        if ("rs232port" in my_configs_dict[item]):
            ports232.append(my_configs_dict[item])
    for item in ports232:
        count = 0
        for item1 in ports232:
            if (item["rs232port"] == item1["rs232port"]):
                count = count + 1
        if (count > 1):
            print("\nFound duplicate use of RS232 port " + str(item["rs232port"]))
            return
    for item in my_configs_dict:
        if ("rs485modbusport" in my_configs_dict[item]):
            ports485.append(my_configs_dict[item])
    for item in ports485:
        count = 0
        for item1 in ports485:
            if (item["rs485modbusport"] == item1["rs485modbusport"]):
                #if (item["useuart232"] != item1["useuart232"]):
                #    count = count + 1
                if (item["rs485modbusbaud"] != item1["rs485modbusbaud"]):
                    count = count + 1
                if (item["rs485modbusparity"] != item1["rs485modbusparity"]):
                    count = count + 1
                if (item["rs485modbusdatabits"] != item1["rs485modbusdatabits"]):
                    count = count + 1
                if (item["rs485modbusstopbits"] != item1["rs485modbusstopbits"]):
                    count = count + 1
        if (count > 0):
            print("\nFound duplicate use of RS485 port with different settings " + str(item["rs485modbusport"]))
            return
    for item in ports485:
        for item1 in ports232:
            if (item["rs485modbusport"] == item["rs232port"]):
                print("\nFound RS485 and RS232 port sharing")
                return
    for item in my_configs_dict:
        if ("usegpioinput" in my_configs_dict[item]):
            gpios_in.append(my_configs_dict[item])
    count1 = 0
    count2 = 0
    count3 = 0
    count4 = 0
    for item in gpios_in:
        #print(item["usegpioinput"])
        if (int(item["usegpioinput"]) == 1):
            count1 = count1 + 1
        if (int(item["usegpioinput"]) == 2):
            count2 = count2 + 1
        if (int(item["usegpioinput"]) == 3):
            count3 = count3 + 1
        if (int(item["usegpioinput"]) == 4):
            count4 = count4 + 1
        if (count1 > 1):
            print("\nFound duplicate use of DigitalIn1")
            return
        if (count2 > 1):
            print("\nFound duplicate use of DigitalIn2")
            return
        if (count3 > 1):
            print("\nFound duplicate use of DigitalIn3")
            return
        if (count4 > 1):
            print("\nFound duplicate use of DigitalIn4")
            return
    for item in my_configs_dict:
        if ("usegpiooutput" in my_configs_dict[item]):
            gpios_out.append(my_configs_dict[item])
    count1 = 0
    count2 = 0
    count3 = 0
    count4 = 0
    print("\n")
    for item in gpios_out:
        #print(item["usegpiooutput"])
        if (int(item["usegpiooutput"]) == 1):
            count1 = count1 + 1
        if (int(item["usegpiooutput"]) == 2):
            count2 = count2 + 1
        if (int(item["usegpiooutput"]) == 3):
            count3 = count3 + 1
        if (int(item["usegpiooutput"]) == 4):
            count4 = count4 + 1
        if (count1 > 2):
            print("Found duplicate use of DigitalOut1 " + str(item["commandname"]))
            return
        if (count2 > 2):
            print("Found duplicate use of DigitalOut2 " + str(item["commandname"]))
            return
        if (count3 > 2):
            print("Found duplicate use of DigitalOut3 " + str(item["commandname"]))
            return
        if (count4 > 2):
            print("Found duplicate use of DigitalOut4 " + str(item["commandname"]))
            return
    
    
def main(argv):
    global my_configs_dict
    try:
        print("\n        Avnet IoTConnectSDK Configuration Utility\n")
        print("                  Component Selector\n")
        print("\n\t\t Configure SDK Components")
        component_selected_dict = {}
        
        config = configparser.ConfigParser()
        config.read('IoTConnectSDK.conf.default')
        my_configs_dict = {s:dict(config.items(s)) for s in config.sections()}
        config.read('IoTConnectSDK.conf')
        my_config_parser_current_dict = {s:dict(config.items(s)) for s in config.sections()}
        my_configs_dict.update(my_config_parser_current_dict)
        count = 0
        count1 = 0
        if (int(my_configs_dict["CloudSystemControl"]["systemconfigured"]) > 0):
            line = raw_input("\n\nDo you want to default the configuration Yes/No: ")
            line = line.rstrip()
            if (line == 'Yes'):
                my_configs_dict["CloudSystemControl"]["systemconfigured"] = "0"
                os.system('cp IoTConnectSDK.conf.default IoTConnectSDK.conf')                    
        #read defaults
        configs = cmdline("find . -name IoTConnectSDK.conf")
        configs = configs.splitlines()
        for item in configs:
            config = configparser.ConfigParser()
            item = item[2:len(item)]
            item = str(item)
            if (item.find("Plugin") != -1):
                config.read(item)
                my_config_parser_plugin_dict = {s:dict(config.items(s)) for s in config.sections()}
                if (int(my_configs_dict["CloudSystemControl"]["systemconfigured"]) == 0):
                    my_configs_dict.update(my_config_parser_plugin_dict)
                    count = 0

        for item1 in my_configs_dict:
            component_selected_dict[count1] = [item1,'IoTConnectSDK.conf', my_configs_dict[item1]["modelversion"]]
            count1 = count1 + 1
        my_configs_dict["CloudSystemControl"]["systemconfigured"] = "1"
        my_configs_desc_dict = {}
        configs_desc = cmdline("find . -name IoTConnectSDK.conf.desc")
        configs_desc = configs_desc.splitlines()
        for item in configs_desc:
            config = configparser.ConfigParser()
            item = item[2:len(item)]
            item = str(item)
            if (item.find("Plugin") != -1):
                config.read(item)
                my_config_parser_desc_dict = {s:dict(config.items(s)) for s in config.sections()}
                my_configs_desc_dict.update(my_config_parser_desc_dict)
        config.read("IoTConnectSDK.conf.desc")
        my_config_parser_desc_dict = {s:dict(config.items(s)) for s in config.sections()}
        my_configs_desc_dict.update(my_config_parser_desc_dict)
        
        count = 0
        while True:
            for item in component_selected_dict:
                print(str(count) + ": " + str(component_selected_dict[count][0]) + "\033[50D\033[50CVersion=" + str(component_selected_dict[count][2]))
                count = count + 1
                if (((count % 16) == 0) or (count == len(component_selected_dict))):
                    break
            check_configuration()
            if (count == len(component_selected_dict)):
                line = input_choice("Selection","Exit")
            else:
                if (count > 16):
                    line = input_choice("Selection","More/Back")
                else:
                    line = input_choice("Selection","More")
            if (line == 'More'):
                continue
            if (line == 'Back'):
                count = count - 32
                continue
            if (line == 'Exit'):
                break
            if (str.isdigit(line) == True):
                print("Last_change = " + str(line))
                last_change = int(line)
            print("\n")
            this_selection = my_configs_dict[component_selected_dict[int(line)][0]]
            selected = component_selected_dict[int(line)][0]
            while True:
                count1 = 0
                for item in my_configs_dict[component_selected_dict[int(line)][0]]:
                    print(count)
                    if (str(my_configs_desc_dict[str(selected)][item]) != "*"):
                        print(str(count1) + " " + str(item) + "=" + str(this_selection[item]) + "\n\tDesc: " + str(my_configs_desc_dict[selected][item]) + str("\n"))
                    count1 = count1 + 1
                change = input_choice("Selection", "Back or Delete")
                change = str(change)
                found = 0
                if ( 'Back' == change.strip()):
                    print("\033[2J\033[H")
                    if (len(component_selected_dict) == count):
                        count = count - ((len(component_selected_dict)) % 16)
                    else:
                        count = count - 16
                    break
                if ( 'Delete' == change.strip()):
                    print(str(last_change))
                    print(str(component_selected_dict[int(last_change)][0]))
                    my_configs_dict.pop(str(component_selected_dict[int(last_change)][0]))
                    #component_selected_dict.pop(int(last_change))
                    count2 = 0
                    component_selected_dict = {}
                    for item in my_configs_dict:
                        print(item)
                        component_selected_dict[count2] = [item, 'unknown',my_configs_dict[item]["modelversion"]]
                        count2 = count2 + 1
                    count = 0
                    break
                count2 = 0
                for item in my_configs_dict[component_selected_dict[int(line)][0]]:
                    if (str(my_configs_desc_dict[str(selected)][item]) != "*"):
                        if (int(count2) == int(change)):
                            found = 1
                    count2 = count2 + 1
                    if (found == 1):
                        value = raw_input("Enter new value for " + item + " " + " : ")
                               
                        this_selection[item] = value
                        my_configs_dict[component_selected_dict[int(line)][0]][item] = value
                        print("Item changed: "+ item + " "+ value)
                        break
        print("Writing Configurations")
        parser = configparser.ConfigParser()        
        for item in my_configs_dict:
            parser.add_section(str(item))
            for item1 in my_configs_dict[item]:
                parser.set(item, item1, my_configs_dict[item][item1])
        with open('IoTConnectSDK.conf', 'w') as f:
            parser.write(f)
            
        print("Done.")
        print("Copy the files in this directory to your gateway /opt/avnet-iot/IoTConnect/sample")
    except Exception as ex:
        exc_type, exc_value, exc_traceback = sys.exc_info()
        traceback.print_tb(exc_traceback)
        print(ex)
 
if __name__ == "__main__":
    main(sys.argv)
