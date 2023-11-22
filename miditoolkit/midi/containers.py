import re
import warnings
from dataclasses import dataclass
from typing import List, Optional, Union

from ..constants import MAJOR_NAMES, MINOR_NAMES


@dataclass
class Note:
    """A note event.

    Parameters
    ----------
    velocity : int
        Note velocity.
    pitch : int
        Note pitch, as a MIDI note number.
    start : int
        Note on time, absolute, in ticks.
    end : int
        Note off time, absolute, in ticks.

    """

    velocity: int
    pitch: int
    start: int
    end: int

    @property
    def duration(self) -> int:
        """Get the duration of the note in ticks."""
        return self.end - self.start


@dataclass
class Pedal:
    """A pedal event.

    Parameters
    ----------
    start : int
        Time when the pedal starts.
    end : int
        Time when the pedal ends.

    """

    start: int
    end: int

    @property
    def duration(self) -> int:
        return self.end - self.start


@dataclass
class PitchBend:
    """A pitch bend event.

    Parameters
    ----------
    pitch : int
        MIDI pitch bend amount, in the range ``[-8192, 8191]``.
    time : int
        Time when the pitch bend occurs.

    """

    pitch: int
    time: int


@dataclass
class ControlChange:
    """A control change event.

    Parameters
    ----------
    number : int
        The control change number, in ``[0, 127]``.
    value : int
        The value of the control change, in ``[0, 127]``.
    time : int
        Time when the control change occurs.

    """

    number: int
    value: int
    time: int


@dataclass
class TimeSignature:
    """Container for a Time Signature event, which contains the time signature
    numerator, denominator and the event time in ticks.

    Attributes
    ----------
    numerator : int
        Numerator of time signature.
    denominator : int
        Denominator of time signature.
    time : int
        Time of event in ticks.

    Examples
    --------
    Instantiate a TimeSignature object with 6/8 time signature at the tick 384:

    >>> ts = TimeSignature(6, 8, 384)
    >>> print ts
    6/8 at the tick 384

    """

    numerator: int
    denominator: int
    time: int

    def __post_init__(self):
        if self.numerator <= 0:
            raise ValueError(f"{self.numerator} is not a valid `numerator` value")
        if self.denominator <= 0:
            raise ValueError(f"{self.denominator} is not a valid `denominator` value")
        if self.time < 0:
            raise ValueError(f"{self.time} is not a valid `time` value")

    def __str__(self):
        return f"{self.numerator}/{self.denominator} at {self.time:d} ticks"


@dataclass
class KeySignature:
    """Contains the key signature and the event time in ticks.
    Only supports major and minor keys.

    Attributes
    ----------
    key_name : str
        Key number according to ``[0, 11]`` Major, ``[12, 23]`` minor.
        For example, 0 is C Major, 12 is C minor.
    time : int
        Time of event in ticks.

    Examples
    --------
    Instantiate a C# minor KeySignature object at the tick 384:

    >>> ks = KeySignature("C#", 384)
    >>> print ks
    C# minor at the tick 384
    """

    key_name: str
    time: int

    def __post_init__(self):
        if self.time < 0:
            raise ValueError(f"{self.time} is not a valid `time` value")

        self.key_number = _key_name_to_key_number(self.key_name)
        if not (0 <= self.key_number < 24):
            raise ValueError(
                f"{self.key_number} is not a valid `key_number` type or value"
            )

    def __str__(self):
        return f"{self.key_name} [{self.key_name}] at {self.time:d} ticks"


@dataclass
class Marker:
    text: str
    time: int

    def __repr__(self):
        return 'Marker(text="{}", time={})'.format(
            self.text.replace('"', r"\""), self.time
        )

    def __str__(self):
        return f'"{self.text}" at {self.time:d} ticks'


@dataclass
class Lyric:
    """TContains the key signature and the event time in ticks.
    Only supports major and minor keys.


    Attributes
    ----------
    text : str
        The text of the lyric.
    time : int
        The time in ticks of the lyric.
    """

    text: str
    time: int

    def __repr__(self):
        return 'Lyric(text="{}", time={})'.format(
            self.text.replace('"', r"\""), self.time
        )

    def __str__(self):
        return f'"{self.text}" at {self.time:d} ticks'


@dataclass
class TempoChange:
    """Container for a Tempo event, which contains the tempo in BPM and the event time in ticks.

    Attributes
    ----------
    tempo : int
        Tempo value.
    time : int
        Time of event in ticks.

    Examples
    --------
    Instantiate a Tempo object with BPM=120 at the tick 384:

    >>> ts = TempoChange(120, 384)
    >>> print ts
    Tempo of 120 bpm at the tick 384.

    """

    tempo: Union[float, int]
    time: int

    def __str__(self):
        return f"{self.tempo} BPM at {self.time:d} ticks"


class Instrument:
    """Object to hold event information for a single instrument.

    Parameters
    ----------
    program : int
        MIDI program number (instrument index), in ``[0, 127]``.
    is_drum : bool
        Is the instrument a drum instrument (channel 9)?
    name : str
        Name of the instrument.

    Attributes
    ----------
    program : int
        The program number of this instrument.
    is_drum : bool
        Is the instrument a drum instrument (channel 9)?
    name : str
        Name of the instrument.
    notes : list
        List of :class:`miditoolkit.Note` objects.
    pitch_bends : list
        List of :class:`miditoolkit.PitchBend` objects.
    control_changes : list
        List of :class:`miditoolkit.ControlChange` objects.

    """

    def __init__(
        self,
        program: int,
        is_drum: bool = False,
        name: str = "",
        notes: Optional[List[Note]] = None,
        pitch_bends: Optional[List[PitchBend]] = None,
        control_changes: Optional[List[ControlChange]] = None,
        pedals: Optional[List[Pedal]] = None,
    ):
        """Create the Instrument."""
        self.program = program
        self.is_drum = is_drum
        self.name = name
        self.notes = [] if notes is None else notes
        self.pitch_bends = [] if pitch_bends is None else pitch_bends
        self.control_changes = [] if control_changes is None else control_changes
        self.pedals = [] if pedals is None else pedals

    def remove_invalid_notes(self, verbose: bool = True) -> None:
        warnings.warn(
            "Call remove_notes_with_no_duration() instead.",
            DeprecationWarning,
            stacklevel=2,
        )
        return self.remove_notes_with_no_duration()

    def remove_notes_with_no_duration(self) -> None:
        """Removes (inplace) notes whose end time is before or at their start time."""
        for i in range(self.num_notes - 1, -1, -1):
            if self.notes[i].start >= self.notes[i].end:
                del self.notes[i]

    @property
    def num_notes(self) -> int:
        return len(self.notes)

    def __repr__(self):
        return f"Instrument(program={self.program}, is_drum={self.is_drum}, name={self.name}) - {self.num_notes} notes"

    def __eq__(self, other):
        # Here we check all tracks attributes except the name.
        # The list attributes will be checked sequentially one by one, this means that
        # if two Instrument objects have the same musical content, but with some elements in
        # different orders (for example two notes with swapped indices in a list), the method will
        # return False. To make this method insensible to the lists orders, you can manually sort
        # them before calling it: `track.notes.sort(key=lambda x: (x.start, x.pitch, x.end, x.velocity))`.
        # The same can be done for control_changes, pitch_bends and pedals.
        if self.is_drum != other.is_drum or self.program != other.program:
            return False

        # Check list attributes.
        # These list should all contain objects that is either a dataclass or implements `__eq__`.
        lists_attr = [name for name, val in vars(self).items() if isinstance(val, list)]
        for list_attr in lists_attr:
            if len(getattr(self, list_attr)) != len(getattr(other, list_attr)):
                return False
            if any(
                a1 != a2
                for a1, a2 in zip(getattr(self, list_attr), getattr(other, list_attr))
            ):
                return False

        # All good, both tracks holds the exact same content
        return True


def _key_name_to_key_number(key_string: str) -> int:
    # Create lists of possible mode names (major or minor)
    # Construct regular expression for matching key
    pattern = re.compile(
        # Start with any of A-G, a-g
        "^(?P<key>[ABCDEFGabcdefg])"
        # Next, look for #, b, or nothing
        "(?P<flatsharp>[#b]?)"
        # Allow for a space between key and mode
        " ?"
        # Next, look for any of the mode strings
        "(?P<mode>(?:(?:" +
        # Next, look for any of the major or minor mode strings
        ")|(?:".join(MAJOR_NAMES + MINOR_NAMES)
        + "))?)$"
    )
    # Match provided key string
    result = re.match(pattern, key_string)
    if result is None:
        raise ValueError(f"Supplied key {key_string} is not valid.")
    # Convert result to dictionary
    result = result.groupdict()

    # Map from key string to pitch class number
    key_number = {"c": 0, "d": 2, "e": 4, "f": 5, "g": 7, "a": 9, "b": 11}[
        result["key"].lower()
    ]
    # Increment or decrement pitch class if a flat or sharp was specified
    if result["flatsharp"]:
        if result["flatsharp"] == "#":
            key_number += 1
        elif result["flatsharp"] == "b":
            key_number -= 1
    # Circle around 12 pitch classes
    key_number = key_number % 12
    # Offset if mode is minor, or the key name is lowercase
    if result["mode"] in MINOR_NAMES or (
        result["key"].islower() and result["mode"] not in MAJOR_NAMES
    ):
        key_number += 12

    return key_number
