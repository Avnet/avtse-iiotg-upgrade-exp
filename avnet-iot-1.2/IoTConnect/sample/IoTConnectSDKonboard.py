import threading
import traceback
import sys
import json
import time

from datetime import datetime
global SendDataArray
global SendDataLock
global PushDataNow
global PushDataArray
global sdk
global callbackChain
callbackChain = []
global callbackTwinChain
callbackTwinChain = []
global RegisterCallbackMsg
global RegisterCallbackTwinMsg
global IoTConnectConnecting
global serial_number

 
PushDataNow = 0
PushDataArray = []
SendDataArray = []
SendDataLock = threading.Lock()

def __init__(self,myglobals):
    globals().update(myglobals)
    #print("OnBoard Globals" + str(myglobals))

if (sys.version_info[0] < 3):
    import httplib
    from urlparse import urlparse
    def service_call(method, url, header=None, body=None):
        try:
            parsed_uri = urlparse(url)
            scheme = parsed_uri.scheme
            host = parsed_uri.hostname
            port = parsed_uri.port
            path = parsed_uri.path
        
            if parsed_uri.query:
                path = '%s?%s' % (path, parsed_uri.query)
        
            if port == None:
                if scheme == "http":
                    conn = httplib.HTTPConnection(host)
                else:
                    conn = httplib.HTTPSConnection(host)
            else:
                if scheme == "http":
                    conn = httplib.HTTPConnection(host, port)
                else:
                    conn = httplib.HTTPSConnection(host, port)
        
            if body == None:
                if header != None:
                    conn.request(method, path, headers=header)
                else:
                    conn.request(method, path)
        
            if body != None:
                body = json.dumps(body)
                if header != None:
                    conn.request(method, path, body, headers=header)
                else:
                    conn.request(method, path, body)
        
            response = conn.getresponse()
            data = None
            if response.status == 200:
                data = response.read()
                data = json.loads(data.decode('utf-8'))
            else:
                if response.status == 204:
                    return None
                else:
                    myprint("Bad http response: " + str(response.status))
                    myprint("  " + str(method) + " " + str(url) + " " + str(header) + " " + str(body) + str(response))
        except Exception as ex:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            traceback.print_tb(exc_traceback)
            myprint(ex)
            sys.stdout.flush()
            sys.stderr.flush()
            myprint("No network")
        finally:
            conn.close()
            return data
else:
    import http.client
    from urllib.parse import urlparse
    def service_call(method, url, header=None, body=None):
        try:
            parsed_uri = urlparse(url)
            scheme = parsed_uri.scheme
            host = parsed_uri.hostname
            port = parsed_uri.port
            path = parsed_uri.path
        
            if parsed_uri.query:
                path = '%s?%s' % (path, parsed_uri.query)
        
            if port == None:
                if scheme == "http":
                    conn = http.client.HTTPConnection(host)
                else:
                    conn = http.client.HTTPSConnection(host)
            else:
                if scheme == "http":
                    conn = http.client.HTTPConnection(host, port)
                else:
                    conn = http.client.HTTPSConnection(host, port)
        
            if body == None:
                if header != None:
                    conn.request(method, path, headers=header)
                else:
                    conn.request(method, path)
        
            if body != None:
                body = json.dumps(body)
                if header != None:
                    conn.request(method, path, body, headers=header)
                else:
                    conn.request(method, path, body)
        
            response = conn.getresponse()
            data = None
            if response.status == 200:
                data = response.read()
                data = json.loads(data.decode('utf-8'))
            else:
                if response.status == 204:
                    return None
                else:
                    myprint("Bad http response: " + str(response.status))
                    myprint("  " + str(method) + " " + str(url) + " " + str(header) + " " + str(body) + str(response))
        except Exception as ex:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            traceback.print_tb(exc_traceback)
            myprint(ex)
            sys.stdout.flush()
            sys.stderr.flush()
            myprint("No network")
        finally:
            conn.close()
            return data
                            

    
def get_auth(username, password, solution_key):
    try:
        access_token = None
        data = None
        authToken = service_call("GET", AUTH_BASEURL + "/auth/basic-token")
        if authToken != None:
            data = str(authToken["data"])
        if data != None:
            body = {}
            body["username"] = username
            body["password"] = password
            header = {
                "Content-type": "application/json",
                "Accept": "*/*",
                "Authorization": 'Basic %s' % data,
                "Solution-key": solution_key
            }
            data = service_call("POST", AUTH_BASEURL + "/auth/login", header, body)
            if data != None:
                access_token = str('Bearer %s' % data["access_token"])
        return access_token
    except:
        return None

def get_template(searchText):
    global ACCESS_TOKEN
    try:
        header = {
            "Content-type": "application/json",
            "Accept": "*/*",
            "Authorization": ACCESS_TOKEN
        }

        templates = []
        response = service_call("GET", TEMPLATE_BASEURL + "/device-template?searchText=%s" % searchText, header)
        if response != None and response["data"] != None and len(response["data"]) > 0:
            templates = response["data"]
        
        if len(templates) > 0:
            return templates[0]
        else:
            return None
    except:
        return None

global GetAccessToken
def GetAccessToken():
    global ACCESS_TOKEN,AUTH_BASEURL,TEMPLATE_BASEURL,DEVICE_BASEURL
    global my_config_parser_dict, my_sensor_dict, my_command_dict
    global uniqueId
    global template
    global serial_number
    global EndorsementKey
    global deviceTemplateGuid
    global template_name 
    #QA API
    AUTH_BASEURL = my_config_parser_dict["CloudSystemControl"]["http_auth_token"]
    TEMPLATE_BASEURL = my_config_parser_dict["CloudSystemControl"]["http_device_template"]
    DEVICE_BASEURL= my_config_parser_dict["CloudSystemControl"]["http_device_create"]
    username = my_config_parser_dict["CloudSystemControl"]["username"]
    #password = keyring.get_password(service_id, username)
    password = my_config_parser_dict["CloudSystemControl"]["password"]
    solution_key = my_config_parser_dict["CloudSystemControl"]["solution-key"]
    ACCESS_TOKEN = get_auth(username, password, solution_key)
    if ACCESS_TOKEN == None:
        myprint("authentication failed")
        #sys.exit(1)
        return 0
    #---------------------------------------------------------------------
    template_name = "zt" + str(serial_number)
    available_name = str(my_config_parser_dict["CloudSystemControl"]["template_name"])
    if (available_name != ""):
        template_name = available_name
    header = {
        "Content-type": "application/json",
        "Accept": "*/*",
        "Authorization": ACCESS_TOKEN
    }
    #---------------------------------------------------------------------
    # Get template attribute by searchText
    myprint(template_name)
    template = get_template(template_name)
    if template != None:
        myprint("Device template already exist...")
        deviceTemplateGuid = template['guid']
    return 1

def CloudSetupFirmware():
    global ACCESS_TOKEN,AUTH_BASEURL,TEMPLATE_BASEURL,DEVICE_BASEURL
    global my_config_parser_dict, my_sensor_dict, my_command_dict
    global uniqueId
    global serial_number
    global EndorsementKey
    global template
    global isedge
    global isgateway
    global templateDescription
    global template_name
    global deviceTemplateGuid
    myprint("Setting up firmware")
    header = {
            "Content-type": "application/json",
            "Accept": "*/*",
            "Authorization": ACCESS_TOKEN
    }
    firmware = []
    found = 0
    response = service_call("GET", "https://firmware.iotconnect.io/api/v2/firmware?Name=%s" % str(template_name), header)
    if response != None and response["data"] != None and len(response["data"]) > 0:
        firmware = response["data"]
        myprint(firmware)
        for item in firmware:
            if (str(item['name']) == str(template_name).upper()):
                found = 1
                myprint("FoundFW")
                response = service_call("GET", "https://firmware.iotconnect.io/api/v2/firmware/%s" % item['guid'], header)
                exists = 0
                myprint(response['data'])
                for version in response['data'][0]['Upgrades']:
                    if (str(version['software']) == str(my_config_parser_dict["CloudDeviceFirmware"]["software"])):
                        exists = 1
                        myprint("ExistsFW")
                if (exists == 0):
                    if (str(my_config_parser_dict["CloudDeviceFirmware"]["developermode"]) == "1"):
                        myprint("Adding software upgrade entry for version " + str(my_config_parser_dict["CloudDeviceFirmware"]["software"]))
                        body = {
                            "firmwareGuid": item['guid'],
                            "firmwareDescription": str(my_config_parser_dict["CloudDeviceFirmware"]["firmwaredescription"]),
                            "software": str(my_config_parser_dict["CloudDeviceFirmware"]["software"])
                            #"tag": for gateways
                        }
                        response = service_call("POST", "https://firmware.iotconnect.io/api/v2/firmware-upgrade" , header, body)
                        if response != None and response["data"] != None and len(response["data"]) > 0:
                            myprint("Added firmware entry")
                            myprint("Add file for this and publish on web portal")
                        else:
                            myprint("Firmware add failed" + str(response))
                        
                    else:
                        myprint("Need to manually create upgrade on web portal")
        #myprint(firmware)
    if (found == 0):
        body = {
            "deviceTemplateGuid": deviceTemplateGuid,
            "firmwareName": str(template_name).upper(),
            "firmwareDescription": str(my_config_parser_dict["CloudDeviceFirmware"]["firmwaredescription"]),
            "hardware": str(my_config_parser_dict["CloudDeviceFirmware"]["hardware"]),
            "software": str(my_config_parser_dict["CloudDeviceFirmware"]["software"])
            #"firmwarefile": str(my_config_parser_dict["CloudDeviceFirmware"]["firmwarefile"])
        }
        myprint("Adding firmware entry")
        response = service_call("POST", "https://firmware.iotconnect.io/api/v2/firmware" , header, body)
        if response != None and response["data"] != None and len(response["data"]) > 0:
            myprint("Added firmware entry")
        else:
            myprint("Firmware failed" + str(response))


def CloudConfigureDevice():
    global ACCESS_TOKEN,AUTH_BASEURL,TEMPLATE_BASEURL,DEVICE_BASEURL
    global my_config_parser_dict, my_sensor_dict, my_command_dict
    global uniqueId
    global serial_number
    global EndorsementKey
    global template
    global isedge
    global isgateway
    global templateDescription
    global template_name
    global deviceTemplateGuid
    isedge = 0
    isgateway = 0 
    if template != None:
        return
    #---------------------------------------------------------------------
    # Create new template
    template_name = "zt" + str(serial_number)
    available_name = str(my_config_parser_dict["CloudSystemControl"]["template_name"])
    if (available_name != ""):
        template_name = available_name
    templateDescription = "SmartEdgeIIoTGateway"
    myprint(template_name)
    if (str(my_config_parser_dict["CloudSystemControl"]["isedgesupport"]) == "1"):
        templateDescription = "SmartEdgeIIoTGatewayEdge"
        isedge = 1
    if (str(my_config_parser_dict["CloudSystemControl"]["isgatewaysupport"]) == "1"):
        if (isedge == 1):
            templateDescription = "SmartEdgeIIoTGatewayEdgeGateway"
        else:
            templateDescription = "SmartEdgeIIoTGatewayGateway"
        isgateway = 1
    #CloudSetupFirmware()
    myprint("Edge: " + str(isedge) + " Gateway: " + str(isgateway))
    templateDescription = templateDescription + str(serial_number)        
    template = []
    header = {
        "Content-type": "application/json",
        "Accept": "*/*",
        "Authorization": ACCESS_TOKEN
    }
    if ((isedge == 1) and (isgateway == 0)):
        body = {
            "name": template_name,
            "description": str(templateDescription),
            "code": template_name,
            "isEdgeSupport": isedge,
            "attributes": 0,
            "attrXml": 0,
            "firmwareguid":  "",
            "authType": int(my_config_parser_dict["CloudSystemControl"]["authtype"]),
        } 
    elif ((isgateway == 1) and (isedge == 0)):
        body = {
            "name": template_name,
            "description": str(templateDescription),
            "code": template_name,
            "isEdgeSupport": isedge,
            "isType2Support": isgateway,
            "tag": template_name,
            "attributes": 0,
            "attrXml": 0,
            "firmwareguid":  "",
            "authType": int(my_config_parser_dict["CloudSystemControl"]["authtype"]),
        }
    elif ((isgateway == 1) and (isedge == 1)):
        body = {
            "name": template_name,
            "description": str(templateDescription),
            "code": template_name,
            "isEdgeSupport": isedge,
            "isType2Support": isgateway,
            "tag": template_name,
            "attributes": 0,
            "attrXml": 0,
            "firmwareguid":  "",
            "authType": int(my_config_parser_dict["CloudSystemControl"]["authtype"]),
        }
    else:
 
        body = {
            "name": template_name,
            "description": str(templateDescription),
            "firmwareguid": "",
            "code": template_name,
            "isEdgeSupport": isedge,
            "authType": int(my_config_parser_dict["CloudSystemControl"]["authtype"]),
        }   
    response = service_call("POST", TEMPLATE_BASEURL + "/device-template", header, body)
    if response != None and response["data"] != None and len(response["data"]) > 0:
        deviceTemplateGuid = str(response["data"][0]["deviceTemplateGuid"])
    myprint("TemplateCreated")
    if deviceTemplateGuid == None:
        myprint("Failed to create device template...")
        return
    myprint(deviceTemplateGuid)
 
    header = {
        "Content-type": "application/json",
        "Accept": "*/*",
        "Authorization": ACCESS_TOKEN
    }

    # Get attributes
    #attributes = {}
    #attributes = GetAttributes()
    #myprint("GotAttributes")
    #section = "CloudSDKDefaultObject"
    for item in my_config_parser_dict:
        if (str(item).find("Object") != -1):
            create = 0
            #for attr in attributes:
            #   if (attr["localname"] == name):
            #        create = 1
            #        break
            if (create == 0):
                myprint("Adding Object " + my_config_parser_dict[item]["name"])
                response = AddAttribute(my_config_parser_dict[item])
                name = my_config_parser_dict[item]["name"]
                if response != None and response["data"] != None:
                    myprint("Created " + name)
                else:
                    myprint("Couldn't Create Attribute " + name + " Response " + str(response))
                usepythoninterface = my_config_parser_dict[item]["usepythoninterface"]
                my_sensor_dict[item]["name"] = name
                my_sensor_dict[item]["usepythoninterface"] = usepythoninterface
                my_sensor_dict[item]["heartbeatreload"] = int(my_config_parser_dict[item]["reportheartbeatcount"])
                my_sensor_dict[item]["type"] = my_config_parser_dict[item]['value']
                report = my_config_parser_dict[item]["report"]            
                my_sensor_dict[item]["report"] = report
                reportpolltime = my_config_parser_dict[item]["reportpolltime"]            
                my_sensor_dict[item]["reportheartbeatcount"] = my_config_parser_dict[item]["reportheartbeatcount"]
                my_sensor_dict[item]["reportpolltime"] = reportpolltime    
                my_sensor_dict[item]["pushdataalways"] = int(my_config_parser_dict[item]["pushdataalways"])

    myprint("Added Attributes")
    #commands = {}
    #response = GetCommands()
    #if response != None and response["data"] != None:
    #    commands = response["data"]
    for item in my_config_parser_dict:
        if (str(item).find("Command") != -1):
            myprint("Adding Command " + my_config_parser_dict[item]["commandname"])
            #for item1 in commands:
            #    if (str(item1['command'] == str(item1['command']))):
            #        #Found no need to add
            #        continue
            response = AddCommand(my_config_parser_dict[item])
            if response != None and response["data"] != None:
                my_command_dict[my_config_parser_dict[item]["command"]] = my_config_parser_dict[item]["usepythoninterface"]           
            myprint("Commands added")
        
    Enroll()
    myprint("Done Enrolling!")

def CloudSetupObjects():
    global ACCESS_TOKEN,AUTH_BASEURL,TEMPLATE_BASEURL,DEVICE_BASEURL
    global my_config_parser_dict, my_sensor_dict, my_command_dict, my_rules_dict
    global uniqueId
    global template
    global template_name
    global templateDescription
    global deviceTemplateGuid
    role = my_config_parser_dict["CloudSystemControl"]["role"]

    header = {
        "Content-type": "application/json",
        "Accept": "*/*",
        "Authorization": ACCESS_TOKEN
    }
    if template == None:
        myprint("Device template does not exist Configuring and Registering Device on Cloud!")
        CloudConfigureDevice()
        myprint("CloudConfigured")
        template = get_template(template_name)
        if template != None:
            deviceTemplateGuid = template['guid']
            return
    myprint("CloudConfigured")
    for item in my_config_parser_dict:
        if (str(item).find("Object") != -1):
            name = my_config_parser_dict[item]["name"]
            usepythoninterface = my_config_parser_dict[item]["usepythoninterface"]
            my_sensor_dict[item]["name"] = name
            my_sensor_dict[item]["usepythoninterface"] = usepythoninterface
            my_sensor_dict[item]["reportheartbeatcount"] = my_config_parser_dict[item]["reportheartbeatcount"] 
            report = my_config_parser_dict[item]["report"]            
            my_sensor_dict[item]["report"] = report
            reportpolltime = my_config_parser_dict[item]["reportpolltime"]            
            my_sensor_dict[item]["type"] = my_config_parser_dict[item]['value']
            my_sensor_dict[item]["heartbeatreload"] = int(my_config_parser_dict[item]["reportheartbeatcount"])
            my_sensor_dict[item]["reportpolltime"] = reportpolltime    
            my_sensor_dict[item]["pushdataalways"] = int(my_config_parser_dict[item]["pushdataalways"])    #while (count != 0):
            name = my_config_parser_dict[item]["name"]
    # check for device existance
    NeedsEnrolled = 1
    response = service_call("GET", str(my_config_parser_dict["CloudSystemControl"]["http_device_template"])+"/Device" , header)
    if response != None and response["data"] != None and len(response["data"]) > 0:
        cloud_devices = response["data"]
        
        for item in cloud_devices:
            if(uniqueId == item['uniqueId']):
                NeedsEnrolled = 0

    if ((int(my_config_parser_dict["CloudSystemControl"]["systemconfigured"]) !=2)):
        datatype = None
        response = service_call("GET", TEMPLATE_BASEURL + "/device-template/datatype", header)
        if response != None and response["data"] != None and len(response["data"]) > 0:
            datatype = {}
            for d in response["data"]:
                datatype[d["name"]] = d["guid"]
    
        attributes = []
        response = GetAttributes()
        if response != None and response["data"] != None and len(response["data"]) > 0:
            attributes = response["data"]
    
        for item in my_config_parser_dict:
            if (str(item).find("Object") != -1):
                name = my_config_parser_dict[item]["name"]
                usepythoninterface = my_config_parser_dict[item]["usepythoninterface"]
                my_sensor_dict[item]["name"] = name
                my_sensor_dict[item]["usepythoninterface"] = usepythoninterface
                my_sensor_dict[item]["reportheartbeatcount"] = my_config_parser_dict[item]["reportheartbeatcount"] 
                report = my_config_parser_dict[item]["report"]            
                my_sensor_dict[item]["report"] = report
                reportpolltime = my_config_parser_dict[item]["reportpolltime"]            
                my_sensor_dict[item]["type"] = my_config_parser_dict[item]['value']
                my_sensor_dict[item]["heartbeatreload"] = int(my_config_parser_dict[item]["reportheartbeatcount"])
                my_sensor_dict[item]["reportpolltime"] = reportpolltime    
                my_sensor_dict[item]["pushdataalways"] = int(my_config_parser_dict[item]["pushdataalways"])    #while (count != 0):
                name = my_config_parser_dict[item]["name"]
                create = 0
                for attr in attributes:
                    if (attr["localname"] == name):
                        create = 1
                        break
                if (create == 0):
                    response = AddAttribute(my_config_parser_dict[item])

                    if response != None and response["data"] != None:
                        myprint("Created " + name)
                    else:
                        myprint("Couldn't Create Attribute " + name)
        myprint("Template Updated")
        attributes = []
        response = GetAttributes()
        if response != None and response["data"] != None and len(response["data"]) > 0:
            attributes = response["data"]
        myprint("Checking for delete")
        myprint("\n")
        for item in my_config_parser_dict:
            if (str(item).find("Object") == -1):
                continue 
            delete = 0
            for attr in attributes:
                name = my_config_parser_dict[item]['name']
                if (str(attr['localname']) == str(name)):
                    myprint("Assigned " + str(name))
                    delete = 1
            if (delete == 0):
                attributeGuid = str(attr["guid"]) 
                response = DeleteAttribute(attributeGuid)
                if response != None and response["data"] != None:
                    myprint("Deleted " + attr["localname"])
        myprint("Attributes synced with Cloud")
        commands = {}
        response = GetCommands()
        if response != None and response["data"] != None and len(response["data"]) > 0:
            commands = response["data"]

        for item in my_config_parser_dict:
            found = 0
            if (str(item).find("Command") != -1):
                if (commands != None):
                    for item1 in commands:
                        if (str(my_config_parser_dict[item]['command']) == str(item1['command'])):
                            # Found no need to add
                            found = 1
                    if (found == 0):
                        myprint("AddingCommand: " + str(my_config_parser_dict[item]))
                        response = AddCommand(my_config_parser_dict[item])
                    if response != None and response["data"] != None:
                        myprint("Created " + str(item1['command']))
                    else:   
                        myprint("Couldn't Create Command " + str(item1['command']))
                my_command_dict[my_config_parser_dict[item]["command"]] = my_config_parser_dict[item]["usepythoninterface"]           
        myprint("Commands synced with cloud")
        entityguid = my_config_parser_dict["CloudSystemControl"]["entity_guid"]
        entityguid = str(entityguid)

        attributes = []
        response = service_call("GET", str(my_config_parser_dict["CloudSystemControl"]["http_rule_template"])+"/Rule" , header)
        if response != None and response["data"] != None and len(response["data"]) > 0:
            attributes = response["data"]
        device_name = uniqueId
        severity_levels = []
        response = service_call("GET", str(my_config_parser_dict["CloudSystemControl"]["http_event_template"])+"/severity-level/lookup" , header)
        if response != None and response["data"] != None and len(response["data"]) > 0:
            severity_levels = response["data"]

        user_guid = 0  
        cloud_users = []
        response = service_call("GET", str(my_config_parser_dict["CloudSystemControl"]["http_user_template"])+"/user/lookup" , header)
        if response != None and response["data"] != None and len(response["data"]) > 0:
            cloud_users = response["data"]
        for item in cloud_users:
            if (item['userid'] == my_config_parser_dict["CloudSystemControl"]["username"]):
                user_guid = item['guid']

        cloud_roles = []
        response = service_call("GET", str(my_config_parser_dict["CloudSystemControl"]["http_user_template"])+"/role/lookup" , header)
        if response != None and response["data"] != None and len(response["data"]) > 0:
            cloud_roles = response["data"]
        role_guid = 0
        for role in cloud_roles:
            if (role['name'] == my_config_parser_dict["CloudSystemControl"]["role"]):
                role_guid = role['guid']
        cloud_devices = []
        myprint("Template name " + str(template_name))
        templateGuid = template['guid']
        cloud_devices = []
        response = service_call("GET", str(my_config_parser_dict["CloudSystemControl"]["http_device_template"])+"/device/lookup" , header)
        if response != None and response["data"] != None and len(response["data"]) > 0:
            cloud_devices = response["data"]
        for item in cloud_devices:
            if(device_name == item['uniqueId']):
                device_guid = item['guid']

        cloud_commands = []
        response = service_call("GET", TEMPLATE_BASEURL + "/template-command/%s/lookup" % deviceTemplateGuid, header)
        if response != None and response["data"] != None and len(response["data"]) > 0:
            cloud_commands = response["data"]
        cloud_rules = []
        response = service_call("GET", TEMPLATE_BASEURL + "/Rule" , header)
        if response != None and response["data"] != None and len(response["data"]) > 0:
            cloud_rules = response["data"]
        #myprint("CloudRules: " + str(cloud_rules))
        for item in my_config_parser_dict:
            if (str(item).find("Rule") != -1):
                location = my_config_parser_dict[item]["rulelocation"]
                if (location == "Local"):
                    myprint("Setup Local Rule")
                    my_rules_dict[item]["name"] = my_config_parser_dict[item]["name"]            
                    my_rules_dict[item]["sensor"] = my_config_parser_dict[item]["sensor"]
                    my_rules_dict[item]["command"] = my_config_parser_dict[item]["command"]
                    my_rules_dict[item]["condition"] = my_config_parser_dict[item]["condition"]
                    my_rules_dict[item]["conditionvalue"] = my_config_parser_dict[item]["conditionvalue"]
                elif (location == "Cloud"):
                    myprint("Setup Cloud Rule")
                    name = my_config_parser_dict[item]["name"]  
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
                        #myprint("CloudCommands: " + str(cloud_commands))
                        #myprint("Severity: " + str(severity_levels))
                        for item1 in cloud_commands:
                            if(item1['name'] == my_config_parser_dict[item]["command"]):
                                cloud_command_guid = item1['guid']
                                for level in severity_levels:
                                    if (level["SeverityLevel"] == my_config_parser_dict[item]["severity"]):
                                        severity_guid = level["guid"]
                                        #myprint("Found Severity")
                                    body = {
                                        "name": name, 
                                        "templateGuid": templateGuid,
                                        "ruleType": int(my_config_parser_dict[item]["ruletype"]),
                                        "severityLevelGuid": severity_guid,
                                        "conditionText": str(my_config_parser_dict[item]["condition"]),
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
                                    response = service_call("POST",str(my_config_parser_dict["CloudSystemControl"]["http_rule_template"] + "/Rule"), header, body)
                                    if response != None and response["data"] != None:
                                        myprint("Created " + name)
                                    else:
                                        myprint("Response " + str(response))
                                        myprint("Couldnt Create Rule " + name)
                                #else:
                                    #myprint("Severity Incorrect")
                        #else:
                            #myprint("Command Not Found " + str(item1['name']))
    myprint("Rules synced with Cloud")
    if (NeedsEnrolled == 1):
        Enroll()

def AddAttribute(config_dict):
    #myprint("Rules : " + str(GetRules()))
    # Get Attributes the check to see if add needed.
    response = GetAttributes()
    add_attribute = 0
    if (response == None):
        add_attribute = 1
    else:
        attributes = response["data"]
    if (add_attribute == 0):
        found = 0
        for item in attributes:
            if (item["localname"] == config_dict["name"]):
                found = 1
        if (found == 0):
            add_attribute = 1
    response = None # for return at end if not adding because found
    if (add_attribute == 1):        
        header = {
            "Content-type": "application/json",
            "Accept": "*/*",
            "Authorization": ACCESS_TOKEN
        }
        datatype = None
        response = service_call("GET", TEMPLATE_BASEURL + "/device-template/datatype", header)
        if response != None and response["data"] != None and len(response["data"]) > 0:
            datatype = {}
            for d in response["data"]:
                datatype[d["name"]] = d["guid"]
        if len(datatype) == 0:
            return
        aggType = str(config_dict['edgeaggregatetype'])
        Tumble = str(config_dict['edgetumblingwindow'])
        gatewaytagged = int(config_dict['gatewaytagged'])
        childname = str(config_dict['childname'])
        #build body based on edge/gateway
        if ((isedge == 1) and (isgateway == 0)):
            body = {
                "localName": config_dict['name'],
                "deviceTemplateGuid": deviceTemplateGuid,
                "unit" : str(config_dict["units"]) ,
                "description": str(config_dict['description']),
                "dataTypeGuid": datatype[config_dict["value"]],
                "aggregateType": aggType.split(),
                #"tag": template_name,
                "attributes": [],
                "tumblingWindow": Tumble       
            }
        elif (isgateway == 1):
            if (gatewaytagged == 1):
                body = {
                    "localName": config_dict['name'],
                    "deviceTemplateGuid": deviceTemplateGuid,
                    "unit" : str(config_dict["units"]) ,
                    "description": str(config_dict['description']),
                    "dataTypeGuid": datatype[config_dict["value"]],
                    "tag": template_name,
                    "attributes": [],
                }
            else:
                body = {
                    "localName": childname,
                    "deviceTemplateGuid": deviceTemplateGuid,
                    "unit" : str(config_dict["units"]) ,
                    "description": str(config_dict['description']),
                    "dataTypeGuid": datatype[config_dict["value"]],
                    "tag": childname,
                    "attributes": [],
                }
            
        else:
            body = {
                "localName": config_dict['name'],
                "deviceTemplateGuid": deviceTemplateGuid,
                "unit" : str(config_dict["units"]) ,
                "description": str(config_dict['description']),
                "dataTypeGuid": datatype[config_dict["value"]],
                "attributes": [],
            }

            response = service_call("POST", TEMPLATE_BASEURL + "/template-attribute", header, body)
    return(response)

def Enroll():

    endorsementKey = EndorsementKey
    header = {
        "Content-type": "application/json",
        "Authorization": ACCESS_TOKEN
    }
    display_name = my_config_parser_dict["CloudSystemControl"]["display_name"]
    display_name_id = str(serial_number)
    if not display_name:
        display_name = "IoTGateway " + display_name_id
    entityguid = my_config_parser_dict["CloudSystemControl"]["entity_guid"]
    entityguid = str(entityguid)
        
    # TODO Add test to see if gateway needs to populated child devices
    body = {
    "deviceTemplateGuid":deviceTemplateGuid,
    "displayName":display_name,
    "endorsementKey":endorsementKey,
    "entityGuid":entityguid,
    "note":"test",
    "uniqueID":uniqueId
    }
        
    response = service_call("POST", TEMPLATE_BASEURL + "/device", header, body)
    if response != None and response["data"] != None and len(response["data"]) > 0:
        myprint("enrolled")
    else:
        myprint("enroll failed")
        myprint(str(response))
    response = service_call("GET", TEMPLATE_BASEURL + "/Device/lookup", header)
    if response != None and response["data"] != None and len(response["data"]) > 0:
        devices = response["data"]
        myprint("Devices Found")
        #myprint(devices)
    else:
        myprint("Error No Devices Found")
    #uniqueIdGateway = my_config_parser_dict["CloudSystemControl"]["uniqueidgateway"]
    #GatewayTemplatename = my_config_parser_dict["CloudSystemControl"]["gateway_template_name"]
    #myprint(GatewayTemplatename)
    #myprint(devices)
    template = get_template(template_name)
    if template != None:
        myprint("Device Gateway Template Exists")
        deviceTemplateGatewayGuid = template['guid']
        for item in devices:
            if (item['uniqueId'] == uniqueId):
                myprint("Found gateway")
                myprint(item)
                myprint(item['uniqueId'])
                myprint(item['displayName'])
                myprint(item['parentDeviceGuid'])
                parentDeviceGuid = item['guid']
                myprint(item['guid'])
                parentDeviceGuid = item['guid']
            # look up gateway template guid
    else:
        print("GatewayNotFound " + GatewayTemplatename)
        return
    # find sensors and do this if gatewaytagged = 0
    for item in my_config_parser_dict:
        if (str(item).find("Object") != -1):
            if (str(my_config_parser_dict[item]['gatewaytagged']) == "0"):
                body = {
                    "deviceTemplateGuid":deviceTemplateGatewayGuid,
                    "displayName":my_config_parser_dict[item]['name'],
                    "entityGuid":entityguid,
                    "note":"test",
                    "tag":str(my_config_parser_dict[item]['childname']),
                    "parentDeviceGuid": parentDeviceGuid,
                    "uniqueId":my_config_parser_dict[item]['name'] + "C"
                }
                myprint(body)
                response = service_call("POST", TEMPLATE_BASEURL + "/device", header, body)
                if response != None and response["data"] != None and len(response["data"]) > 0:
                    myprint("child enrolled")
                else:
                    myprint("child enroll failed")
                    myprint(str(response))

 
def AddCommand(config_dict):
    global deviceTemplateGuid
    global ACCESS_TOKEN
    global TEMPLATE_BASEURL
    # Get commands
    response = GetCommands()
    if (response == None):
        add_command = 1
    else:
        commands = response["data"]
        add_command = 0
    if (add_command == 0):
        found = 0
        for item in commands:
            if (item["command"] == config_dict["command"]):
                found = 1
        if (found == 0):
            add_command = 1
    response = None # for return at end if not adding because found
    if (add_command == 1):            
        header = {
            "Content-type": "application/json",
            "Accept": "*/*",
            "Authorization": ACCESS_TOKEN
        }

        body = {
            "name": str(config_dict["commandname"]),
            "deviceTemplateGuid": deviceTemplateGuid,
            "command": str(config_dict["command"]),
            "requiredParam": int(config_dict["hasparameter"]),
            "requiredAck": int(config_dict["requiresack"]),
            "isOTACommand": int(config_dict["isiotcommand"])
            #        "cmdText": str(config_dict["cmdText"])
        }
        myprint("AddCommand body " + str(body))
        response = service_call("POST", TEMPLATE_BASEURL + "/template-command", header, body)
    
    return response

def AddRule(config_dict):
    attributes = []
    response = service_call("GET", str(my_config_parser_dict["CloudSystemControl"]["http_rule_template"])+"/Rule" , header)
    if response != None and response["data"] != None and len(response["data"]) > 0:
        attributes = response["data"]
    device_name = uniqueId
    severity_levels = []
    response = service_call("GET", str(my_config_parser_dict["CloudSystemControl"]["http_event_template"])+"/severity-level/lookup" , header)
    if response != None and response["data"] != None and len(response["data"]) > 0:
        severity_levels = response["data"]

    user_guid = 0
    cloud_users = []
    response = service_call("GET", str(my_config_parser_dict["CloudSystemControl"]["http_user_template"])+"/user/lookup" , header)
    if response != None and response["data"] != None and len(response["data"]) > 0:
        cloud_users = response["data"]
    for item in cloud_users:
        if (item['userid'] == my_config_parser_dict["CloudSystemControl"]["username"]):
            user_guid = item['guid']

    cloud_roles = []
    response = service_call("GET", str(my_config_parser_dict["CloudSystemControl"]["http_user_template"])+"/role/lookup" , header)
    if response != None and response["data"] != None and len(response["data"]) > 0:
        cloud_roles = response["data"]
    role_guid = 0
    for role in cloud_roles:
        if (role['name'] == my_config_parser_dict["CloudSystemControl"]["role"]):
            role_guid = role['guid']
    myprint("Template name: " + str(template_name) + " " + str(deviceTemplateGuid))
#    templateGuid = template['guid']

    cloud_devices = []
    response = service_call("GET", str(my_config_parser_dict["CloudSystemControl"]["http_device_template"])+"/device/lookup" , header)
    if response != None and response["data"] != None and len(response["data"]) > 0:
        cloud_devices = response["data"]
    for item in cloud_devices:
        if(device_name == item['uniqueId']):
            device_guid = item['guid']

    cloud_commands = []
    response = service_call("GET", TEMPLATE_BASEURL + "/template-command/%s/lookup" % deviceTemplateGuid, header)
    if response != None and response["data"] != None and len(response["data"]) > 0:
        cloud_commands = response["data"]
    location = config_dict["rulelocation"]
    if (location == "Local"):
        myprint("Setup Local Rule")
        my_rules_dict[item]["name"] = config_dict["name"]            
        my_rules_dict[item]["sensor"] = config_dict["sensor"]
        my_rules_dict[item]["command"] = config_dict["command"]
        my_rules_dict[item]["condition"] = config_dict["condition"]
        my_rules_dict[item]["conditionvalue"] = config_dict["conditionvalue"]
    elif (location == "Cloud"):
        myprint("Setup Cloud Rule")
        name = config_dict["name"]  
        myprint("Creating")
        severity_guid = 0
        cloud_command_guid = 0
        for item1 in cloud_commands:
            if(item1['name'] == config_dict["command"]):
                cloud_command_guid = item1['guid']
                for level in severity_levels:
                    if (level["SeverityLevel"] == config_dict["severity"]):
                        severity_guid = level["guid"]
                        body = {
                            "name": name, 
                            "templateGuid": templateGuid,
                            "ruleType": int(config_dict["ruletype"]),
                            "severityLevelGuid": severity_guid,
                            "conditionText": str(config_dict["condition"]),
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
                        response = service_call("POST",str(my_config_parser_dict["CloudSystemControl"]["http_rule_template"] + "/Rule"), header, body)
                        if response != None and response["data"] != None:
                            myprint("Created " + name)
                        else:
                            myprint("Response " + str(response))
                            myprint("Couldnt Create Rule " + name)

def GetCommands():
    global ACCESS_TOKEN
    global TEMPLATE_BASEURL
    header = {
        "Content-type": "application/json",
        "Accept": "*/*",
        "Authorization": ACCESS_TOKEN
    }
    response = service_call("GET", TEMPLATE_BASEURL + "/template-command/%s/lookup" % deviceTemplateGuid , header)
    return response

def GetAttributes():
    header = {
        "Content-type": "application/json",
        "Accept": "*/*",
        "Authorization": ACCESS_TOKEN
    }
    response = service_call("GET", TEMPLATE_BASEURL + "/template-attribute/%s/lookup" % deviceTemplateGuid, header)
    return response

def GetRules( ):
    header = {
        "Content-type": "application/json",
        "Accept": "*/*",
        "Authorization": ACCESS_TOKEN
    }
    response = service_call("GET", TEMPLATE_BASEURL + "/Rule", header)
    return response

def DeleteAttribute(attributeGuid):
    header = {
        "Content-type": "application/json",
        "Accept": "*/*",
        "Authorization": ACCESS_TOKEN
    }

    response = service_call("DELETE", TEMPLATE_BASEURL + "/template-attribute/%s" % attributeGuid, header)
    return response

def DeleteCommand(attributeGuid):
    header = {
        "Content-type": "application/json",
        "Accept": "*/*",
        "Authorization": ACCESS_TOKEN
    }  
    response = service_call("DELETE", TEMPLATE_BASEURL + "/template-command/%s" % attributeGuid, header)
    return response

def DeleteRule(attributeGuid):
    header = {
        "Content-type": "application/json",
        "Accept": "*/*",
        "Authorization": ACCESS_TOKEN
    }

    response = service_call("DELETE", TEMPLATE_BASEURL + "/Rule/%s" % attributeGuid, header)
    return response


#
# Callbacks section
#



def RegisterCallbackMsg(callbackMessage):
    global callbackChain
    callbackChain.append(callbackMessage)
    

def RegisterCallbackTwinMsg(callbackTwinMessage):
    global callbackTwinChain
    callbackTwinChain.append(callbackTwinMessage)

#
# data processing section
#
def QueueSensorValue(name, my_config_dict, value ,lastvalue):
    global my_sensor_dict
    global PushDataArray
    global PushDataNow
    global SendDataArray
    pushdataalways = int(my_sensor_dict[name]["pushdataalways"])
    try :
        data = {}
        if (int(my_config_dict["precision"]) != 0):
            data[my_sensor_dict[name]["name"]] = round(float(value), int(my_config_dict["precision"]))
        else:
            data[my_sensor_dict[name]["name"]] = value

        if (my_sensor_dict[name]["type"] == "OBJECT"):
            obj = {
                "uniqueId": uniqueId,
                "time": datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S.000Z"),
                "data": value
            }
        else:
            obj = {
                "uniqueId": uniqueId,
                "time": datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S.000Z"),
                "data": data
                }
        SendDataLock.acquire()
        printdata = 0
        if (my_sensor_dict[name]["report"] == "Polled"):    
            if(pushdataalways == 1):
                PushDataArray.append(obj)
                PushDataNow = 1
                printdata = 1
            else:
                SendDataArray.append(obj)
                printdata = 1
        elif (my_sensor_dict[name]["report"] == "OnChange"):
            my_sensor_dict[name]["reportheartbeatcount"] = int(my_sensor_dict[name]["reportheartbeatcount"]) - 1
            if (my_sensor_dict[name]["reportheartbeatcount"] == 0):
                SendDataArray.append(obj)
                PushDataNow = 1
                printdata = 1

                lastvalue = value
                my_sensor_dict[name]["reportheartbeatcount"] = my_sensor_dict[name]["heartbeatreload"]
            else:
                if (lastvalue != value):
                    if(pushdataalways == 1):
                        PushDataArray.append(obj)
                        PushDataNow = 1
                        printdata = 1
                    else:
                        SendDataArray.append(obj)
                        printdata = 1
                    lastvalue = value
        SendDataLock.release()
        if (printdata == 1):
            myprint(str(my_sensor_dict[name]["name"]) + "=" + str(value) + " " + str(obj['time']).rstrip('\n'))            
    
    except Exception as ex:
        if (SendDataLock.locked() == True):
           SendDataLock.release()
        exc_type, exc_value, exc_traceback = sys.exc_info()
        traceback.print_tb(exc_traceback)
        myprint(ex)
        sys.stdout.flush()
        sys.stderr.flush()
        myprint(ex)
        myprint(ex.message)
        myprint("Exception in QueueValue")
    except KeyboardInterrupt:
        if (SendDataLock.locked() == True):
           SendDataLock.release()
        exc_type, exc_value, exc_traceback = sys.exc_info()
        traceback.print_tb(exc_traceback)
        myprint(ex)
        sys.stdout.flush()
        sys.stderr.flush()
        myprint(ex.message)
        myprint("Exception in QueueValue")
    return lastvalue

def SendDataToCloud(name):
    global my_config_parser_dict
    global MessageCount
    global AccessOK
    global count
    global PushDataNow
    global PushDataArray
    global SendDataArray
    global sdk
    RefreshBasicToken = 0
    time.sleep(10)
    myprint("Sending to cloud Task started")
    green = 1
    count = int(my_config_parser_dict["CloudSystemControl"]["sendtocloudrate"])
    try:
        while(True):
            ledprocess = cmdline("/opt/avnet-iot/iotservices/iotstat | grep led")
            if (ledprocess == ""):
                if (green == 1):
                    os.system('echo 0 >/sys/class/leds/red/brightness')
                    os.system('echo 1 >/sys/class/leds/green/brightness')
                    green = 0
                else:
                    os.system('echo 0 >/sys/class/leds/red/brightness')
                    os.system('echo 0 >/sys/class/leds/green/brightness')
                    green = 1
            RefreshBasicToken = RefreshBasicToken + 1
            if (RefreshBasicToken > int(my_config_parser_dict["CloudSystemControl"]["renewaccesstoken"])):
                myprint("Refreshing Access Token")
                AccessOK = GetAccessToken()
                RefreshBasicToken = 0

            count = count - 1
            SendDataLock.acquire()
            if (PushDataNow == 1):
                PushDataNow = 0
                if (len(PushDataArray) != 0):
                    MessageCount = MessageCount + 1
                    sdk.SendData(PushDataArray)
                    PushDataArray = []
            if (count == 0):
                count = int(my_config_parser_dict["CloudSystemControl"]["sendtocloudrate"])
                if (len(SendDataArray) != 0):
                    MessageCount = MessageCount + 1
                    sdk.SendData(SendDataArray)
                    SendDataArray = []
            time.sleep(float(1))
            SendDataLock.release()

    except Exception as ex:
        exc_type, exc_value, exc_traceback = sys.exc_info()
        traceback.print_tb(exc_traceback)
        myprint(ex)
        myprint("SendDataToCloud Exit")
    print("SendDataToCloudExit")


#
# Utilities and Initializations
#
def Watchdogthread():
    myprint(cmdline('/opt/avnet-iot/iotservices/startwd'))
    myprint("Using ATTINY Watchdog pet every 30 seconds")
    while 1:
        time.sleep(int(my_config_parser_dict["CloudSystemControl"]["useiotwatchdog"]))
        cmdline('echo t | tee /dev/watchdog1')
    myprint("Stopping ATTINY Watchdog.")
    myprint(cmdline('echo V | tee /dev/watchdog1'))

def ConnAckWatcher():
    try:
        while 1:
            out = subprocess.Popen(["journalctl", "-n", "1", "-u", "iotconnectservice"], stdout=PIPE)
            stdoutdata, stderrdata = out.communicate()
            if "mqtt_client timed out waiting for CONNACK" in str(stdoutdata):
                myprint("Azure SDK error (Conn Ack), restarting IoTConnect to fix..")
                os._exit(0)
            if "Connection Not Accepted: 0x5: Not Authorized" in str(stdoutdata):
                myprint("Cloud connection error, restarting IoTConnect service to try to fix.  Also, please check your subscription status.")
                os._exit(0)
            time.sleep(1)
    except Exception as ex:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            traceback.print_tb(exc_traceback)
            myprint(ex)

def MonitorSDKStartupError(item):
    global IoTConnectConnecting
    while(1):
        
        time.sleep(60)
        if (IoTConnectConnecting == 1):
            myprint("failed to connect, letting systemd restart us")
            os._exit(0)
            
def Start(sdkpassed):
    global sdk
    sdk = sdkpassed
    #x1 = threading.Thread(target=MonitorSDKStartupError, args=("TPM issue thread",))
    #x1.daemon = True
    #x1.start()
    if (int(my_config_parser_dict["CloudSystemControl"]["useiotwatchdog"]) == 1):
        x2 = threading.Thread(target=Watchdogthread)
        x2.daemon = True
        x2.start()
    x3 = threading.Thread(target=ConnAckWatcher, name='Journal Watcher')
    x3.daemon = True
    x3.start()
    x4 = threading.Thread(target=SendDataToCloud, args=("Sending",))
    x4.daemon = True
    x4.start()
    myprint("Monitor and Sending threads started")
