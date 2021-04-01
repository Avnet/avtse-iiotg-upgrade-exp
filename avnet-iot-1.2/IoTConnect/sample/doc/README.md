# SmartEgde IIOT Gateway SDK Plugins

Version 1.2 of the SmartEdge IIOT Gateway Cloud SDK contains a new concept called plugins.  Simple put if you put your code in a directory called IoTPluginXXX... The SDK will automatically find it and setup the cloud with the appropriate information.  Note, you must keep the format and for new sensors please use one of the provided Templates.


## Getting Started

The new tool IoTConnectSDKConfigure has installed and setup the new Python SDK .  To control it use either "iotstart,iotstop,iotrestart" or "sudo systemctl restart iotconnectservice.service"  Once the SDK is running your data will show up on your cloud device.  Please read supporting SmartEdge documents for more detailed information

### Prerequisites
None

### Installing


This portion SDK will get installed by the IoTConnectSDKConfigure tool.  It contains the new SDK engine and documentation as well as a system configuration setup for needed tools.


## Deployment

If the IoTConnectSDKConfigure tool was run on a standard linux box you must copy the files over to your SmartEdge Gateway in the directory you specified as the startup directory.

## Versioning

This is version 1.0 of the Python Plugin Cloud SDK

## License

This project is licensed under the SmartEdge IIOT Gateway license.
