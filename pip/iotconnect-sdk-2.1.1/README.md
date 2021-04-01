# Softweb Solutions Inc
## IOT Connect SDK : Software Development Kit 1.0.0

**Prerequisite tools:**

1. Python : Python version 2.7, 3.6 and 3.7
2. pip : pip is compatible to the python version
3. setuptools : Required to install IOTConnect SDK

**Installation for python vesion 2.7:**

1. Extract the "iotconnect-sdk-python-v1.0.0.zip"

2. To install the required libraries use the below command:
	- Goto SDK directory path using terminal/Command prompt
	- cd iotconnect-sdk/
    - pip install iotconnect-sdk-2.0.tar.gz

3. Using terminal/command prompt goto sample folder
	- cd iotconnect-sdk/sample 

4. Ready to go: //This script can send the data to given input(uniqueid, cpid) device by command prompt
    - python example_py2.py <<env>> //Environment DEV, QA, POC, AVNETPOC, PROD (Default if not supply the environment argument) - Python 2.* compatible
    - python example_py3.py <<env>> //Environment DEV, QA, POC, AVNETPOC, PROD (Default if not supply the environment argument) - Python 3.6 and 3.7 compatible
    
**Usage :**

Import library
```python
from iotconnect import IoTConnectSDK
```

Prerequisite input data *
```python
scopeId=<<your scopeId>>
uniqueId = <<uniqueId>>
cpid = <<CPID>> 
env = <<env>> // DEV, QA, POC, AVNETPOC, PROD(Default)
```

To get the device information and connect to the device
```python
with IoTConnectSDK(cpId, uniqueId, scopeId, callbackMessage, callbackTwinMessage, env) as sdk:
```

To receive the command from Cloud to Device(C2D) 
```python
def callbackMessage(msg):
    global d2cMsg
    print("\n--- Command Message Received ---")
    cmdType = None
    if msg != None and len(msg.items()) != 0:
        cmdType = msg["cmdType"] if msg["cmdType"] != None else None
    
    # Other Command
    if cmdType == "0x01":
        data = msg["data"] if msg["data"] != None else None
        if data != None:
            d2cMsg = {
                "ackId" : data['ackId'],
                "st" : 6,
                "msg" : "",
                "childId" : ""     # if child than add childid
                }
    
    # Firmware Upgrade
    if cmdType == "0x02":
        data = msg["data"] if msg["data"] != None else None
        if data != None:
            d2cMsg = {
                "ackId" : data['ackId'],
                "st" : 7,
                "msg" : ""
                "childId" : ""     # if child than add childid
            }

#for acknowledgement of command
sdk.SendACK(d2cmsg,time,type)

```

To receive the twin from Cloud to Device(C2D) 
```python
def callbackTwinMessage(msg):
    print(msg)
```

To get the list of attributes
```python
sdk.GetAttributes()
```

Data input format
```python
sendTeledata = [{
    "uniqueId": "123456",
    "time" : '2018-05-24T10:06:17.857Z', //Date format should be as defined
    "data": {
        "temperature": 15.55,
        "humidity" : 27.97,
        "weight" : 36,
        "gyroscope" : {
            'x' : -1.2,
            'y' : 0.25,
            'z' : 1.1,
        }
    }
}]
```

To send the data from Device To Cloud(D2C)
```python
sdk.SendData(sendTeledata)
```

- To configure the secure SSL/x509 connection follow below step for CA or CA Selfsiged certificate
	- Open file : sample/properties.json
    - Set SSL/x509 certificate path for CA sign and Selfsign certificate like as below
    - Set max size of offline storage and no of file generate during store data like as below

```json
{
	"certificate" : { 
		"SSLKeyPath"	: "<< file path >>/key.pem",
		"SSLCertPath"   : "<< file path >>/cert.pem",
		"SSLCaPath"     : "<< file path >>/ca.cert.pem"
    },
    "maxSize": 5,
    "fileCount": 5
}
```
