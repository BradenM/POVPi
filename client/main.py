"""
    POVPi Client 
    main.py
"""

import machine
import time
import BlynkLib
import network
import time
import ujson
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
    "GET_SHADOW": 0,
    "DISPLAY": 1,
    "WRITE_DISPLAY": 2,
    "UPDATE_DISPLAY": 3,
    "POWER": 5,
    "UPDATE_POWER": 6
}

# Device State
STATE = {
    "display": "Hello",
    "enabled": True
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


def update_shadow(new_state):
    '''Updates/Syncs Device Shadow'''
    display = new_state['display']
    power = new_state['enabled']
    if STATE['display'] != display:
        blynk.virtual_write(V['DISPLAY'], display)
        print("New Display: %s" % display)
    if STATE['enabled'] != power:
        blynk.virtual_write(V['POWER'], power)
        print('Power: %s' % power)
    STATE.update(new_state)
    print("State: ", STATE)
    return STATE


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


@blynk.VIRTUAL_WRITE(V['GET_SHADOW'])
def handle_shadow_hook(value):
    '''Update shadow from server'''
    json_data = value[0]
    data = ujson.loads(json_data)
    update_shadow(data)


@blynk.VIRTUAL_WRITE(V['WRITE_DISPLAY'])
def handle_display_update(value):
    '''Handles Display Updates from App'''
    print('Display Update from App')
    data = value[0]
    print("Incoming: ", data)
    blynk.virtual_write(V['UPDATE_DISPLAY'], data)


@blynk.VIRTUAL_WRITE(V['POWER'])
def handle_power_update(value):
    '''Handles Power updates from App'''
    print('Power Update from App')
    data = value[0]
    print("Incoming: ", data)
    blynk.virtual_write(V['UPDATE_POWER'], data)


def main():
    '''Main Event Loop'''
    print("POVPi Ready")
    # Watch Shadow
    timer.set_interval(7, lambda: blynk.virtual_write(V['GET_SHADOW'], 1))

    while 1:
        blynk.run()
        timer.run()


# Start Event Loop
main()
