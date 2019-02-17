"""
    POVPi Client 
    main.py
"""

import machine
import time
import BlynkLib
import network
import time
from timer import BlynkTimer

# Wifi Settings
WIFI = {
    "ssid": "RPIAP",
    "passwd": "raspberrypi"
}

# Server/Blynk Settings
SERVER = {
    "addr": "192.168.4.1",
    "port": 5000,
    "blynk_port": 8080,
    "auth": "4b999209771a4321b80dd0633dc0f2b1"
}

# Virtual Pins
V = {
    "GETSHADOW": 0
}

# Init Timer
timer = BlynkTimer()


def connect_wifi():
    '''Connect to Wifi'''
    ssid = WIFI['ssid']
    passwd = WIFI['passwd']
    wifi = network.WLAN(network.STA_IF)
    wifi.disconnect()
    if wifi.isconnected():
        print("Connected to %s" % ssid)
        get_wifi()
        return wifi
    print("Connecting to %s..." % ssid)
    wifi.active(True)
    wifi.connect(ssid, passwd)
    while not wifi.isconnected():
        pass
    print("Wifi Connected Successfully")
    return get_wifi()


def get_wifi():
    '''Returns Wifi Config Info'''
    wifi = network.WLAN(network.STA_IF)
    if not wifi.isconnected():
        return connect_wifi()
    print("IP: %s" % wifi.ifconfig()[0])
    return wifi


def connect_blynk():
    '''Connects to Blynk Server'''
    auth = SERVER['auth']
    addr = SERVER['addr']
    port = SERVER['blynk_port']
    print("Connecting to Blynk Server @ %s:%s..." % (addr, port))
    time.sleep(5)
    try:
        blynk = BlynkLib.Blynk(auth, server=addr, port=port)
    except Exception as e:
        print("Failed to connect to Blynk, trying again...")
        connect_blynk()
    print("Connected to Blynk Server")
    return blynk


# Startup
print("POVPi Starting...")
wifi = connect_wifi()
blynk = connect_blynk()


# Event Handlers

@blynk.ON("connected")
def handle_blynk_connected(ping):
    '''Event Handler for Blynk Connection'''
    print("Blynk Successfully Connected")
    print("Ping: %sms" % ping)


@blynk.VIRTUAL_WRITE(V['GETSHADOW'])
def handle_shadow_hook(value):
    print('GOT SHADOW', value)


def main():
    '''Main Event Loop'''
    print("POVPi Ready")
    # Watch Shadow
    timer.set_interval(4, lambda: blynk.virtual_write(V['GETSHADOW'], 1))

    while 1:
        blynk.run()
        timer.run()


# Start Event Loop
main()
