# Cisco ZTP Provisioning
This code will turn a Cisco Catalyst 9000 switch into a ZTP provisioning "server".

* Technology stack: Python + Guestshell
* Status:  Alpha, designed to prove the ability and openess of Cisco IOS-XE.

## Supported on Cisco IOS-XE 16.6+
## How to Configure the DHCP pool (on IOS-XE)
```
Device> enable
Device# configure terminal
Device(config)# ip dhcp pool pnp_device_pool
Device(config-dhcp)# network 10.1.1.0 255.255.255.0
Device(config-dhcp)# default-router 10.1.1.1
Device(config-dhcp)# option 67 ascii http://198.51.100.1/http.py
Device(config-dhcp)# end
```
### For more examples
https://www.cisco.com/c/en/us/td/docs/ios-xml/ios/prog/configuration/166/b_166_programmability_cg/zero_touch_provisioning.html

## How to configure guestshell as a server

guestshell portforwarding add table-entry ZTP service tcp source-port 5000 destination-port 5000


## Licensing info
Copyright (c) 2019 Cisco and/or its affiliates.

This software is licensed to you under the terms of the Cisco Sample
Code License, Version 1.1 (the "License"). You may obtain a copy of the
License at

               https://developer.cisco.com/docs/licenses

All use of the material herein must be in accordance with the terms of
the License. All rights not expressly granted by the License are
reserved. Unless required by applicable law or agreed to separately in
writing, software distributed under the License is distributed on an "AS
IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express
or implied.
