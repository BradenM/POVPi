'''
    alpha.py
    Persistence-Of-Vision Raspberry Pi (POVPi)
    Alphanumeric Definitions and functions
'''

from time import sleep

from gpiozero import LED

"""
    LED Definitions
"""
_leds = [26, 19, 13, 6, 5, 9, 11]
leds = [LED(l) for l in _leds]


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
        for i in step:
            leds[i].off()
        sleep(.3)


def display(sentence, interrupt):
    """parses and displays sentence on POVPi"""
    while not interrupt(sentence):
        parsed = sentence.strip()
        for char in sentence:
            if interrupt(sentence):
                break
            char = char.upper()
            print('Display: ', char)
            make_char(char)
        sleep(3)
