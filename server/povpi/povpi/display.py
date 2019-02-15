'''
    povpi/display.py
    Persistence-Of-Vision Raspberry Pi (POVPi)

    Handles formula generation for POVPi
'''

# LED Pin Numbers for Display
leds = [26, 19, 13, 6, 5, 9, 11, 9]


"""
        Alpha Character Definitions
"""
ALPHA = {
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
        [7],
        [7],
        [7],
    ],
    "_SPACE_": [
        [],
        [],
        []
    ]
}


def make_char(char):
    '''create character from alpha formula'''
    if char == " " or char not in ALPHA.keys():
        print(f">> {char} << NOT FOUND")
        print(ALPHA.keys())
        return make_char("_SPACE_")
    print(f"RESOLVING: {char}")

    formula = ALPHA[char]
    leds = [[0 for col in range(8)] for row in range(len(formula))]
    for pos, step in enumerate(formula):
        for i in step:
            leds[pos][i] = 1
    return leds
