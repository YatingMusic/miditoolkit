"""
Author: Wen-Yi Hsiao, Taiwan
"""

__version__ = "1.0.1"

# Convenience exports for commonly used classes.

from miditoolkit.midi.containers import (
    ControlChange,
    Instrument,
    KeySignature,
    Lyric,
    Marker,
    Note,
    Pedal,
    PitchBend,
    TempoChange,
    TimeSignature,
)
from miditoolkit.midi.parser import MidiFile

__all__ = [
    "ControlChange",
    "Instrument",
    "KeySignature",
    "Lyric",
    "Marker",
    "MidiFile",
    "Note",
    "Pedal",
    "PitchBend",
    "TempoChange",
    "TimeSignature",
]
