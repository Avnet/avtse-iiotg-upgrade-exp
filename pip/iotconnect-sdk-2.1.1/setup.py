import os
import sys
from setuptools import setup

packages_requires=["paho-mqtt","ntplib","wheel","azure-iot-provisioning-device-client","azure-iothub-device-client"]
if sys.platform == 'win32':
    packages_requires += ["pypiwin32"]
    
setup(
    name="iotconnect-sdk",
    version="2.1.1",
    python_requires=">=2.7.9,>=3.6,<4",
    description='SDK for D2C and C2D communication',
    license="MIT",
    author='SOFTWEB SOLUTIONS<admin@softwebsolutions.com> (https://www.softwebsolutions.com)',
    packages=["iotconnect", "iotconnect.client", "iotconnect.common"],
    install_requires=packages_requires,
    package_data={'iotconnect': ['assets/*.*']},
    platforms=['Linux', 'Mac OS X', 'Win'],
    zip_safe=False,
    classifiers=[
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "License :: MIT License",
        "Operating System :: OS Independent"
    ],
)
