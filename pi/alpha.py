'''
    alpha.py
    Persistence-Of-Vision Raspberry Pi (POVPi)
    Alphanumeric Definitions and functions
'''

from time import sleep

from gpiozero import LEDBoard

"""
    LED Definitions
"""

leds = LEDBoard(26, 19, 13, 6, 5, 0, 11, 9)

ALPHA = {
    """
        Alpha Character Definitions
    """
    "A": [
        range(2, len(leds)),
        [0, 1, 3, 4],
        [0, 1, 3, 4],
        range(2, len(leds)),
    ],
    "E": [
        range(0, len(leds)),
        [0, 1, 3, 5, 6],
        [0, 1, 3, 5, 6]
    ],
    "L": [
        range(0, len(leds)),
        [6],
        [6],
        [6],
    ]
}


def make_char(char):
    """create character from alpha formula"""
    if char == " " or char not in ALPHA.keys():
        return sleep(1)
    formula = ALPHA[char]
    for step in formula:
        for i in step:
            leds[i].on()
        sleep(.3)
        leds.off()
        sleep(.3)
