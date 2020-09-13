# T-Mobile TV Client

This is a unofficial Python client for T-Mobile TV for watching TV on other IPTV clients.
A webserver is run to keep a session open and providing a m3u playlist and XMLTV EPG for other clients to use.

Most channels requires DRM and will currently only works on Kodi if Widevine is correctly installed.

## Installation
This client requires Python 3 to be installed.
Run the following steps to install the client:

```
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

Copy config.yml.sample to config.yml and insert login credentials and set deviceID to a random value.

## Running
Run the following commands to start the client:

```
source venv/bin/activate
python tmobiletv
```

After starting the client you can download the playlist from http://localhost:5000/api/channels?format=m3u
A XMLTV EPG is available at http://localhost:5000/api/epg?format=xmltv

## Kodi
For Kodi support the following plugins needs to be installed
- [inputstream.adaptive](https://github.com/peak3d/inputstream.adaptive)
- [pvr.iptvsimple](https://github.com/kodi-pvr/pvr.iptvsimple)

To play DRM protected channels the Widevine CDM needs to be correctly installed for inputstream.adaptive.

Use the url http://localhost:5000/api/channels?format=m3u_kodi as playlist in pvr.iptvsimple configuration.
The url http://localhost:5000/api/epg?format=xmltv can be used for the EPG.

Catch-up is supported when running Kodi 19 "Matrix".
For catch-up the EPG needs to be configured and catch-up needs to be enabled in the pvr.iptvsimple plugin.
