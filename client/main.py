"""
    POVPi Client 
    main.py
"""

import time
import esp32

import BlynkLib

import network
import ujson
import _thread as thread
import machine
from machine import Pin, ADC
from timer import BlynkTimer
import micropython as mp

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

# Device Shadow
SHADOW = {
    "display": "Hello",
    "enabled": True,
    "formula": None,
    "ready": True,
}

# Device State
STATE = {
    "LAST_REV": None,
    "COL_TIME": 0,
    "COL_INDEX": 0,
    "PREV_DELTAS": []
}

# Status Messages
STATUS = {
    "BLYNK_CANNOT_CONNECT": (2, 2),
    "READY": (3)
}

# Init Timer
timer = BlynkTimer()

# Init Pins
# A12, A11, A10, A9, A8, A7, A6, GPIO21
# LED_PINS = [13, 12, 27, 33, 15, 32, 14, 21]
LED_PINS = [21, 14, 32, 15, 33, 27, 12, 13]
LEDS = [Pin(i, Pin.OUT, value=0) for i in LED_PINS]

# Battery Analog
BAT_ANALOG = 35

# Hall Effect Setup/Threshold
HALL_THRESHOLD = 300
HALL_PIN = Pin(34, Pin.IN)

# Interrupt Counters
interruptCounter = 0
totalInterrupts = 0


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
        display_status(2, 4)
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
    if SHADOW['display'] != display:
        blynk.virtual_write(V['DISPLAY'], display)
        print("New Display: %s" % display)
    if SHADOW['enabled'] != power:
        blynk.virtual_write(V['POWER'], power)
        print('Power: %s' % power)
    timer.set_timeout(
        4, lambda: blynk.virtual_write(V['FORMULA'], display))
    SHADOW.update(new_state)
    print("State: ", SHADOW)
    return SHADOW


def handle_hall_interrupt(pin):
    '''Handles Hall Effect Interrupt'''
    global interruptCounter
    interruptCounter += 1
    mp.schedule(get_column_rev, pin)


def get_column_rev(pin):
    '''Returns Time in ms for the revolution of a single column'''
    time_start = STATE['LAST_REV']
    time_delta = time.ticks_diff(time.ticks_cpu(), time_start)
    STATE["COL_TIME"] = int(time_delta / 64.00)
    STATE["COL_INDEX"] = 0
    STATE['LAST_REV'] = time.ticks_cpu()
    # print("COLTIME:", col_time)
    return STATE["COL_TIME"]


def display_column(bits, timeout):
    '''Displays singular column from array of bits'''
    cur_column = STATE["COL_INDEX"]
    # if cur_column >= 16 and cur_column <= 48:
    #     bits = list(reversed(bits))
    led_count = len(LEDS)
    while 1:
        if time.ticks_diff(timeout, time.ticks_cpu()) <= 0:
            try:
                for i in range(0, led_count):
                    LEDS[i].value(bits[i])
            except IndexError:
                for o in range(i, led_count):
                    LEDS[o].value(0)
            break

    STATE["COL_INDEX"] += 1

    # print(STATE["COL_INDEX"])


def display():
    '''Displays Text on POVPi'''
    formula = SHADOW['formula']
    enabled = SHADOW['enabled']

    if not formula:
        return

    # Get Times
    col_time = STATE["COL_TIME"]
    display_at = time.ticks_add(time.ticks_cpu(), col_time)
    col_key = STATE["COL_INDEX"]

    # Get Bits
    if col_key < 64:
        display_bits = formula[str(col_key)]
        display_column(display_bits, display_at)
    else:
        [led.value(0) for led in LEDS]

    # Handle Interrupts
    global interruptCounter
    global totalInterrupts
    if interruptCounter > 0:
        state = machine.disable_irq()
        interruptCounter -= 1
        machine.enable_irq(state)
        totalInterrupts += 1


def display_status(times, num=len(LEDS)):
    '''Flashes LEDS to Indicate Status'''
    _LEDS = LEDS[:num]
    for i in range(0, times):
        [led.value(int(not led.value())) for led in _LEDS]
        time.sleep_ms(100)
    [led.value(0) for led in _LEDS]
    return True


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
    # form_len = len(formula.keys())
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


def run_blynk():
    '''Runs Blynk Indefinitely'''
    while 1:
        blynk.run()
        timer.run()


def main():
    '''Main Event Loop'''
    print("POVPi Ready")
    display_status(3)
    # Run Blynk in Thread
    thread.stack_size(5*1024)
    thread.start_new_thread(run_blynk, ())
    # Enable IRQ on Hall Effect
    HALL_PIN.irq(trigger=Pin.IRQ_FALLING, handler=get_column_rev)
    # Test Shadow
    test_shadow = {
        "display": "I",
        "enabled": True
    }
    update_shadow(new_state=test_shadow)
    while 1:
        if SHADOW['ready']:
            if STATE["LAST_REV"] == 0:
                STATE["LAST_REV"] = time.ticks_cpu()
            display()
        else:
            STATE["LAST_REV"] = 0
            STATE["COL_INDEX"] = 0


# Start Event Loop
main()
