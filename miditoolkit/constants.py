""" Constants files

"""

PITCH_RANGE = (0, 127)
PITCH_ID_TO_NAME = {
    0: "C",
    1: "C#",
    2: "D",
    3: "D#",
    4: "E",
    5: "F",
    6: "F#",
    7: "G",
    8: "G#",
    9: "A",
    10: "A#",
    11: "B",
}

MAJOR_NAMES = ["M", "Maj", "Major", "maj", "major"]
MINOR_NAMES = ["m", "Min", "Minor", "min", "minor"]

KEY_NUMBER_TO_MIDO_KEY_NAME = [
    'C', 'Db', 'D', 'Eb', 'E', 'F', 'F#', 'G', 'Ab', 'A', 'Bb', 'B',
    'Cm', 'C#m', 'Dm', 'D#m', 'Em', 'Fm', 'F#m', 'Gm', 'G#m', 'Am',
    'Bbm', 'Bm'
]

DEFAULT_BPM = 120
