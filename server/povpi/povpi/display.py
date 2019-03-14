'''
    povpi/display.py
    Persistence-Of-Vision Raspberry Pi (POVPi)

    Handles formula generation for POVPi
'''
from itertools import chain


"""
        Definitions
"""

# LEDs - GPIO: 21, 14, 26, 15, 25, 27, 12, 13
L = [2097152, 16384, 67108864, 32768, 33554432, 134217728, 4096, 8192]
ALL = sum(L)  # 237039616
ALL_S = sum(L[1:])  # All (Short, minus initial LED)

# Alphanumeric Characters
ALPHA = {
    "_SPACE_": [0, 0, 0, 0, 0, 0],
    "T": [0, L[7], L[7], ALL_S, L[7], L[7]],
    "P": [0, 0, ALL_S, L[7] + L[4], L[7] + L[4], sum(L[4:])],
    "O": [0, 0, ALL_S, L[1] + L[7], L[1] + L[7], ALL_S],
    "V": [0, sum(L[2:]), L[1], L[0], L[1], sum(L[2:])],
    "I": [0, 0, L[1] + L[7], ALL_S, L[1] + L[7], 0]
}

# Special Characters / Displays
SPECIAL = {
    "_LINE_": [ALL, 0, 0, 0, 0, 0]
}


def generate(text):
    '''Generates dict with '''
    parsed = text.strip().upper()
    char_bytes = [ALPHA.get(i, ALPHA["_SPACE_"]) for i in parsed]
    # Flatten List
    char_bytes = list(chain(*char_bytes))
    if parsed in SPECIAL.keys():
        char_bytes = SPECIAL[parsed]
    formula = {index: byte for index, byte in enumerate(char_bytes)}
    return formula
