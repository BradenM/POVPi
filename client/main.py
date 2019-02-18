"""
    POVPi Client 
    main.py
"""

from machine import Pin
import time
import BlynkLib
import network
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
    "UPDATE_POWER": 6,
    "FORMULA": 7,
}

# Device State
STATE = {
    "display": "Hello",
    "enabled": True,
    "formula": None,
    "ready": True
}

# Init Timer
timer = BlynkTimer()

# Init Pins
LED_PINS = [0, 2, 4, 5, 12, 13, 14, 15]
LEDS = [Pin(i, Pin.OUT, value=0) for i in LED_PINS]


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
        connect_blynk()
    print("Connected to Blynk Server")
    return blynk


def update_shadow(new_state=None):
    '''Updates/Syncs Device Shadow'''
    if not new_state:
        return timer.set_timeout(2, lambda: blynk.virtual_write(V["GET_SHADOW"], 1))
    [led.value(0) for led in LEDS]
    display = new_state['display']
    power = new_state['enabled']
    if STATE['display'] != display:
        blynk.virtual_write(V['DISPLAY'], display)
        print("New Display: %s" % display)
    if STATE['enabled'] != power:
        blynk.virtual_write(V['POWER'], power)
        print('Power: %s' % power)
    timer.set_timeout(
        4, lambda: blynk.virtual_write(V['FORMULA'], display))
    STATE.update(new_state)
    print("State: ", STATE)
    return STATE


def display():
    '''Displays Text on POVPi'''
    print('Displaying')
    formula = STATE['formula']
    enabled = STATE['enabled']

    if not formula:
        return

    for char in formula:
        for step in char:
            for pin, value in enumerate(step):
                print("LED: %s @ %s" % (LEDS[pin], value))
                led = LEDS[pin]
                led.value(value)
            print("")


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
    STATE['ready'] = False
    print('Display Update from App')
    data = value[0]
    print("Incoming: ", data)
    blynk.virtual_write(V['UPDATE_DISPLAY'], data)
    update_shadow()


@blynk.VIRTUAL_WRITE(V['POWER'])
def handle_power_update(value):
    '''Handles Power updates from App'''
    STATE['ready'] = False
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
    STATE['formula'] = data['formula']
    power = STATE['enabled']
    if power:
        STATE['ready'] = True


def main():
    '''Main Event Loop'''
    print("POVPi Ready")

    while 1:
        blynk.run()
        timer.run()
        if STATE['ready']:
            display()


# Start Event Loop
main()
