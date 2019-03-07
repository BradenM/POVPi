'''
    povpi/display.py
    Persistence-Of-Vision Raspberry Pi (POVPi)

    Handles formula generation for POVPi
'''
from itertools import chain

# Number of Columns on Display
NUM_COLUMNS = 64


"""
        Alpha Character Definitions
"""
ALPHA = {
    "_SPACE_": [0, 0, 0, 0, 0, 0],
    "E": [0, 31, 21, 21, 0, 0],
    "L": [0, 31, 16, 16, 16, 0],
    # "L": [0, 252, 4, 4, 4, 0],
    "T": [0, 128, 128, 31, 128, 128],
    "N": [0, 31, 4, 8, 16, 31],
    "P": [0, 252, 160, 160, 224, 0],
    "O": [0, 252, 132, 132, 252, 0],
    "V": [0, 240, 48, 8, 48, 240],
    "I": [0, 132, 132, 252, 132, 132],
    "[ALL]": [31, 31, 31, 31, 31, 31]
}


def generate(text):
    '''Generates dict with '''
    parsed = text.strip().upper()
    char_bytes = [ALPHA.get(i, ALPHA["_SPACE_"]) for i in parsed]
    # Flatten List
    char_bytes = list(chain(*char_bytes))
    formula = {index: byte for index, byte in enumerate(char_bytes)}
    return formula
