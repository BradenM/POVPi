"""
    POVPi Client 
    connect.py

    Handles Connectivity and Blynk
"""

import time

import BlynkLib

import network
import ujson

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

# Shadow Handler
SHADOW_HANDLER = None

# Virtual Pins
V = {
    "GET_SHADOW": 0,
    "DISPLAY": 1,
    "WRITE_DISPLAY": 2,
    "UPDATE_DISPLAY": 3,
    "POWER": 5,
    "UPDATE_POWER": 6,
    "FORMULA": 7,
}

# Device Shadow
SHADOW = {
    "display": "Hello",
    "enabled": True,
    "formula": None,
    "ready": True,
}


def connect_wifi():
    '''Connect to Wifi'''
    ssid = WIFI['ssid']
    passwd = WIFI['passwd']
    wifi = network.WLAN(network.STA_IF)
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
        blynk = BlynkLib.Blynk(auth, server=addr, port=port, buffin=2048)
    except Exception as e:
        print("Failed to connect to Blynk, trying again...")
        # display_status(2, 4)
        connect_blynk()
    print("Connected to Blynk Server")
    return blynk


# Setup
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
    SHADOW['ready'] = False
    print('Display Update from App')
    data = value[0]
    print("Incoming: ", data)
    blynk.virtual_write(V['UPDATE_DISPLAY'], data)
    update_shadow()


@blynk.VIRTUAL_WRITE(V['POWER'])
def handle_power_update(value):
    '''Handles Power updates from App'''
    SHADOW['ready'] = False
    print('Power Update from App')
    data = value[0]
    print("Incoming: ", data)
    blynk.virtual_write(V['UPDATE_POWER'], data)
    update_shadow()


@blynk.VIRTUAL_WRITE(V['FORMULA'])
def handle_formula_update(value):
    '''Parses formula from web server'''
    print('Got Formula')
    json_data = value[0]
    data = ujson.loads(json_data)
    dec_formula = data['formula']
    # If formula does not take entire 64 columns, fill the rest with 0s
    form_len = len(dec_formula)
    if form_len < 64:
        for i in range(form_len, 64):
            dec_formula[str(i)] = 0
    # Convert Formula from decimal to binary
    formula = {key: [int(bit) for bit in bin(val)[2:]]
               for key, val in dec_formula.items()}
    SHADOW['formula'] = formula
    power = SHADOW['enabled']
    if power:
        SHADOW['ready'] = True


def set_handler(shadow_handler):
    '''Sets Shadow Handler'''
    SHADOW_HANDLER = shadow_handler
    return (wifi, blynk)
