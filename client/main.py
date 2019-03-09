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
import connect
from connect import V, SHADOW


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
    return STATE["COL_TIME"]


def display_column(bits, timeout):
    '''Displays singular column from array of bits'''
    cur_column = STATE["COL_INDEX"]
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
connection = connect.set_handler(shadow_handler=update_shadow)
wifi = connection[0]
blynk = connection[1]


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
