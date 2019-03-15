"""
    POVPi Client
    main.py
"""

import gc
import time

import _thread as thread
import connect
import machine
from connect import SHADOW, V
from machine import Pin
from timer import BlynkTimer

# Device State
CUR_FORMULA = None
READY = 0
COL_INDEX = 0
COL_TIME = 0

# Global GPIO Reg Vars
GPIO_ODR = {}


# Status Messages
STATUS = {
    "BLYNK_CANNOT_CONNECT": (2, 2),
    "READY": (3)
}

# Init Timer
timer = BlynkTimer()

# Battery Analog
BAT_ANALOG = 35

# Hall Effect Setup/Threshold
HALL_THRESHOLD = 300
HALL_PIN = Pin(34, Pin.IN, Pin.PULL_UP)

# Interrupt Counters
interruptCounter = 0
totalInterrupts = 0


def update_shadow(new_state=None, sync=False):
    '''Updates/Syncs Device Shadow'''
    global READY, CUR_FORMULA
    if sync:
        # Sync Global Variables (performance)
        READY = SHADOW["ready"]
        CUR_FORMULA = memoryview(SHADOW["formula"])
        return SHADOW
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
    # Sync Global Variables (performance)
    READY = SHADOW["ready"]
    return SHADOW


def handle_hall_interrupt(pin):
    '''Handles Hall Effect Interrupt'''
    global interruptCounter
    interruptCounter += 1


def display(byte, col_time, COL_INDEX, GPIO_REG, GPIO_EN, GPIO_CLR, ALL_LEDS):
    '''Displays Text on POVPi'''
    if COL_INDEX < 90:
        cleared = ALL_LEDS - byte
        col_timeout = time.ticks_add(time.ticks_cpu(), col_time*4)
        if byte == 0:
            machine.mem32[GPIO_REG + GPIO_CLR] ^= ALL_LEDS
        else:
            machine.mem32[GPIO_REG + GPIO_CLR] ^= cleared
        machine.mem32[GPIO_REG + GPIO_EN] ^= byte
        while time.ticks_diff(col_timeout, time.ticks_cpu()) >= 0:
            pass
        machine.mem32[GPIO_REG + GPIO_CLR] ^= ALL_LEDS
        return COL_INDEX + 1
    else:
        machine.mem32[GPIO_REG + GPIO_CLR] ^= ALL_LEDS
        return COL_INDEX


def display_status(times, **kwargs):
    '''Flashes LEDS to Indicate Status'''
    for i in range(0, times):
        machine.mem32[GPIO_ODR["REG"] + GPIO_ODR["EN"]] ^= GPIO_ODR["ALL_LEDS"]
        time.sleep_ms(50)
        machine.mem32[GPIO_ODR["REG"] +
                      GPIO_ODR["CLR"]] ^= GPIO_ODR["ALL_LEDS"]
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
    global interruptCounter, totalInterrupts, CUR_FORMULA, READY, GPIO_ODR, COL_INDEX, COL_TIME

    # PINS REGISTERS
    GPIO_REG = const(0x3ff44000)
    GPIO_EN = const(0x8)
    GPIO_CLR = const(0xC)
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
    ALL_LEDS = const(237039616)
    LED_COUNT = const(8)
    GPIO_ODR = {"REG": GPIO_REG, "EN": GPIO_EN, "CLR": GPIO_CLR,
                "ALL_LEDS": ALL_LEDS, "LED_COUNT": LED_COUNT}

    # Last Revolution Time
    LAST_REV = 0

    print("POVPi Ready")
    display_status(9)
    # Run Blynk in Thread
    thread.stack_size(5*1024)
    thread.start_new_thread(run_blynk, ())
    # Startup Shadow
    startup_shadow = {
        "display": "_LINE_",
        "enabled": True
    }
    update_shadow(new_state=startup_shadow)
    gc.collect()
    while 1:
        # Handle Interrupts
        if interruptCounter > 0:
            state = machine.disable_irq()
            interruptCounter -= 1
            machine.enable_irq(state)
            time_delta = time.ticks_diff(time.ticks_cpu(), LAST_REV)
            COL_TIME = int(time_delta / 360)
            COL_INDEX = 0
            LAST_REV = time.ticks_cpu()
            totalInterrupts += 1
        if READY and CUR_FORMULA:
            if LAST_REV == 0:
                LAST_REV = time.ticks_cpu()
            if COL_INDEX < 90:
                byte = CUR_FORMULA[COL_INDEX]
            COL_INDEX = display(byte, COL_TIME, COL_INDEX,
                                GPIO_REG, GPIO_EN, GPIO_CLR, ALL_LEDS)


# Start Event Loop
main()
