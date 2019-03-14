"""
    POVPi Client
    main.py
"""

import time

import _thread as thread
import connect
import machine
import micropython
from connect import SHADOW, V
from machine import Pin
from timer import BlynkTimer
micropython.alloc_emergency_exception_buf(100)

# Device State
STATE = {
    "LAST_REV": None,
    "COL_TIME": 0,
    "COL_INDEX": 0,
}
CUR_FORMULA = None
CUR_INDEX = 0
CUR_TIME = 0

# Status Messages
STATUS = {
    "BLYNK_CANNOT_CONNECT": (2, 2),
    "READY": (3)
}

# Init Timer
timer = BlynkTimer()

# PINS REGISTERS
GPIO_REG = 0x3ff44000
GPIO_EN = 0x8
GPIO_CLR = 0xC
BIT21 = const(1 << 21)  # 2097152
BIT14 = const(1 << 14)  # 16384
BIT26 = const(1 << 26)  # 67108864
BIT15 = const(1 << 15)  # 32768
BIT25 = const(1 << 25)  # 33554432
BIT27 = const(1 << 27)  # 134217728
BIT12 = const(1 << 12)  # 4096
BIT13 = const(1 << 13)  # 8192
LEDS = [BIT21, BIT14, BIT26, BIT15, BIT25, BIT27, BIT12, BIT13]
_LED_PINS = [21, 14, 26, 15, 25, 27, 12, 13]
LED_PINS = [Pin(i, Pin.OUT, value=0) for i in _LED_PINS]
ALL_LEDS = sum(LEDS)  # 237039616
LED_COUNT = len(LEDS)

# Battery Analog
BAT_ANALOG = 35

# Hall Effect Setup/Threshold
HALL_THRESHOLD = 300
HALL_PIN = Pin(34, Pin.IN, Pin.PULL_UP)

# Interrupt Counters
interruptCounter = 0
totalInterrupts = 0


def update_shadow(new_state=None):
    '''Updates/Syncs Device Shadow'''
    if not new_state:
        return timer.set_timeout(2, lambda: blynk.virtual_write(V["GET_SHADOW"], 1))
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


def get_column_rev(pin):
    '''Returns Time in ms for the revolution of a single column'''
    time_start = STATE['LAST_REV']
    time_delta = time.ticks_diff(time.ticks_cpu(), time_start)
    STATE["COL_TIME"] = int(time_delta / 64.00)
    STATE["COL_INDEX"] = 0
    STATE['LAST_REV'] = time.ticks_cpu()
    return STATE["COL_TIME"]


def display_column(byte, timeout):
    '''Displays column on POVPi'''
    cleared = ALL_LEDS - byte
    while 1:
        if time.ticks_diff(timeout, time.ticks_cpu()) <= 0:
            if byte == 0:
                machine.mem32[GPIO_REG + GPIO_CLR] ^= ALL_LEDS
                return True
            machine.mem32[GPIO_REG + GPIO_CLR] ^= cleared
            machine.mem32[GPIO_REG + GPIO_EN] ^= byte
            break


def display(formula, col_index, col_time):
    '''Displays Text on POVPi'''
    if not formula:
        return

    col_timeout = time.ticks_add(time.ticks_cpu(), col_time)
    if col_index < 64:
        display_step = formula[str(col_index)]
        display_column(display_step, col_timeout)


def display_status(times):
    '''Flashes LEDS to Indicate Status'''
    for i in range(0, LED_COUNT):
        machine.mem32[GPIO_REG + GPIO_EN] ^= ALL_LEDS
        time.sleep_ms(50)
        machine.mem32[GPIO_REG + GPIO_CLR] ^= ALL_LEDS
        time.sleep_ms(50)
    return True


# Startup
print("POVPi Starting...")
# Enable IRQ on Hall Effect
HALL_PIN.irq(trigger=Pin.IRQ_FALLING, handler=handle_hall_interrupt)
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
    global interruptCounter, totalInterrupts, CUR_FORMULA
    print("POVPi Ready")
    display_status(3)
    # Run Blynk in Thread
    thread.stack_size(5*1024)
    thread.start_new_thread(run_blynk, ())
    # Test Shadow
    test_shadow = {
        "display": "P",
        "enabled": True
    }
    update_shadow(new_state=test_shadow)
    while 1:
        # Handle Interrupts
        if interruptCounter > 0:
            state = machine.disable_irq()
            interruptCounter -= 1
            machine.enable_irq(state)
            CUR_FORMULA = SHADOW["formula"]
            time_start = STATE['LAST_REV']
            time_delta = time.ticks_diff(time.ticks_cpu(), time_start)
            STATE["COL_TIME"] = int(time_delta / 64.00)
            STATE["COL_INDEX"] = 0
            STATE['LAST_REV'] = time.ticks_cpu()
            totalInterrupts += 1
        if SHADOW["ready"]:
            if STATE["LAST_REV"] == 0:
                STATE["LAST_REV"] = time.ticks_cpu()
            display(CUR_FORMULA, STATE["COL_INDEX"],
                    STATE["COL_TIME"])
            STATE["COL_INDEX"] += 1


# Start Event Loop
main()
