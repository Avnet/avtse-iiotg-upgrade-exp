# remove old SDK
sudo rm example.py
sudo rm Smart_Sensor_IPSO.pyc
sudo rm defaultsections.conf
sudo rm SmartSensor_Modbus.*
sudo rm Smart_Sensor_Registers.*
sudo rm IoTConnectSDK.conf.*
sudo rm Smart_Sensor_Registers.*
sudo rm user_functions.*
sudo rm ZW_REC_Interface.*
sudo rm -R Smart_Sensor
sudo rm  Smart_Sensor_IPSO.*

# Unzip selected SDK components
sudo find . -name '*.zip' -exec unzip -o {} \;

# remove packages
sudo rm *.zip

# TODO Check python version and do additional setups

sudo find . -name setup  -exec /bin/bash {} \;

# add sym link so SDK starts using verison 1.1 system
sudo pip install pycurl
sudo pip install python-can==2.0.0
usermod -a -G dialout root
# run the configuration tool
sudo -E python -u IoTConnectSDKConfigure.py
