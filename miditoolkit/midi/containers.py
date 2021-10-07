import re


class Note(object):
    """A note event.

    Parameters
    ----------
    velocity : int
        Note velocity.
    pitch : int
        Note pitch, as a MIDI note number.
    start : float
        Note on time, absolute, in ticks.
    end : float
        Note off time, absolute, in ticks.

    """

    def __init__(self, velocity, pitch, start, end):
        self.velocity = velocity
        self.pitch = pitch
        self.start = start
        self.end = end

    def get_duration(self):
        """Get the duration of the note in ticks."""
        return self.end - self.start

    def __repr__(self):
        return 'Note(start={:d}, end={:d}, pitch={}, velocity={})'.format(
            self.start, self.end, self.pitch, self.velocity)

class Pedal(object):
    """A pedal event.

    Parameters
    ----------
    start : float
        Time where the pedal starts.
    end : float
        Time where the pedal ends.

    """
    def __init__(self, start, end):
        self.start = start
        self.end = end
        self.duration = end-start
        
    def __repr__(self):
        return 'Pedal(start={:d}, end={:d})'.format(
            self.start, self.end)

class PitchBend(object):
    """A pitch bend event.

    Parameters
    ----------
    pitch : int
        MIDI pitch bend amount, in the range ``[-8192, 8191]``.
    time : float
        Time where the pitch bend occurs.

    """

    def __init__(self, pitch, time):
        self.pitch = pitch
        self.time = time

    def __repr__(self):
        return 'PitchBend(pitch={:d}, time={:d})'.format(self.pitch, self.time)


class ControlChange(object):
    """A control change event.

    Parameters
    ----------
    number : int
        The control change number, in ``[0, 127]``.
    value : int
        The value of the control change, in ``[0, 127]``.
    time : float
        Time where the control change occurs.

    """

    def __init__(self, number, value, time):
        self.number = number
        self.value = value
        self.time = time        

    def __repr__(self):
        return ('ControlChange(number={:d}, value={:d}, time={:d})'.format(self.number, self.value, self.time))


class TimeSignature(object):
    """Container for a Time Signature event, which contains the time signature
    numerator, denominator and the event time in ticks.

    Attributes
    ----------
    numerator : int
        Numerator of time signature.
    denominator : int
        Denominator of time signature.
    time : float
        Time of event in ticks.

    Examples
    --------
    Instantiate a TimeSignature object with 6/8 time signature at 3.14 ticks:

    >>> ts = TimeSignature(6, 8, 3.14)
    >>> print ts
    6/8 at 3.14 ticks

    """

    def __init__(self, numerator, denominator, time):
        if not (isinstance(numerator, int) and numerator > 0):
            raise ValueError(
                '{} is not a valid `numerator` type or value'.format(
                    numerator))
        if not (isinstance(denominator, int) and denominator > 0):
            raise ValueError(
                '{} is not a valid `denominator` type or value'.format(
                    denominator))
        if not (isinstance(time, (int, float)) and time >= 0):
            raise ValueError(
                '{} is not a valid `time` type or value'.format(time))

        self.numerator = numerator
        self.denominator = denominator
        self.time = time

    def __repr__(self):
        return "TimeSignature(numerator={}, denominator={}, time={})".format(
            self.numerator, self.denominator, self.time)

    def __str__(self):
        return '{}/{} at {:d} ticks'.format(
            self.numerator, self.denominator, self.time)


class KeySignature(object):
    """Contains the key signature and the event time in ticks.
    Only supports major and minor keys.

    Attributes
    ----------
    key_number : int
        Key number according to ``[0, 11]`` Major, ``[12, 23]`` minor.
        For example, 0 is C Major, 12 is C minor.
    time : float
        Time of event in ticks.

    Examples
    --------
    Instantiate a C# minor KeySignature object at 3.14 ticks:

    >>> ks = KeySignature(13, 3.14)
    >>> print ks
    C# minor at 3.14 ticks
    """

    def __init__(self, key_name, time):
        if not isinstance(key_name, str):
            raise ValueError(
                '{} is not a valid `key_name` string'.format(
                    key_name))
        if not (isinstance(time, (int, float)) and time >= 0):
            raise ValueError(
                '{} is not a valid `time` type or value'.format(time))

        self.key_name = key_name
        self.key_number = _key_name_to_key_number(key_name)
        if not (self.key_number >= 0 and self.key_number < 24):
            raise ValueError(
                '{} is not a valid `key_number` type or value'.format(
                    self.key_number))
        self.time = time

    def __repr__(self):
        return "KeySignature(key_name={}, key_number={}, time={})".format(
            self.key_name, self.key_number, self.time)

    def __str__(self):
        return '{} [{}] at {:d} ticks'.format(self.key_name, self.key_number, self.time)

class Marker(object):
    def __init__(self, text, time):
        self.text = text
        self.time = time

    def __repr__(self):
        return 'Marker(text="{}", time={})'.format(
            self.text.replace('"', r'\"'), self.time)

    def __str__(self):
        return '"{}" at {:d} ticks'.format(self.text, self.time)

class Lyric(object):
    """TContains the key signature and the event time in ticks.
    Only supports major and minor keys.


    Attributes
    ----------
    text : str
        The text of the lyric.
    time : float
        The time in ticks of the lyric.
    """
    def __init__(self, text, time):
        self.text = text
        self.time = time

    def __repr__(self):
        return 'Lyric(text="{}", time={})'.format(
            self.text.replace('"', r'\"'), self.time)

    def __str__(self):
        return '"{}" at {:d} ticks'.format(self.text, self.time)


class TempoChange(object):
    """Container for a Tempo event, which contains the tempo in BPM and the event time in ticks.

    Attributes
    ----------
    numerator : int
        Numerator of time signature.
    denominator : int
        Denominator of time signature.
    time : float
        Time of event in ticks.

    Examples
    --------
    Instantiate a Tempo object with BPM=120 at 3.14 ticks:

    >>> ts = Tempo(120, 3.14)
    >>> print ts
    6/8 at 3.14 ticks

    """

    def __init__(self, tempo, time):
        self.tempo = tempo
        self.time = time

    def __repr__(self):
        return "TempoChange(tempo={}, time={})".format(
            self.tempo, self.time)

    def __str__(self):
        return '{} BPM at {:d} ticks'.format(self.tempo, self.time)


class Instrument(object):
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
        List of :class:`pretty_midi.Note` objects.
    pitch_bends : list
        List of of :class:`pretty_midi.PitchBend` objects.
    control_changes : list
        List of :class:`pretty_midi.ControlChange` objects.

    """

    def __init__(self, program, is_drum=False, name=''):
        """Create the Instrument.

        """
        self.program = program
        self.is_drum = is_drum
        self.name = name
        self.notes = []
        self.pitch_bends = []
        self.control_changes = []
        self.pedals = []

    def remove_invalid_notes(self, verbose=True):
        """Removes any notes whose end time is before or at their start time.

        """
        # Crete a list of all invalid notes
        notes_to_delete = []
        for note in self.notes:
            if note.end <= note.start:
                notes_to_delete.append(note)
        if verbose:
            if len(notes_to_delete):
                print('\nInvalid notes:')
                print(notes_to_delete, '\n\n')
            else:
                print('no invalid notes found')
            return True

        # Remove the notes found
        for note in notes_to_delete:
            self.notes.remove(note)
        return False

    def __repr__(self):
        return 'Instrument(program={}, is_drum={}, name="{}")'.format(
            self.program, self.is_drum, self.name.replace('"', r'\"'))
    

def _key_name_to_key_number(key_string):
    # Create lists of possible mode names (major or minor)
    major_strs = ['M', 'Maj', 'Major', 'maj', 'major']
    minor_strs = ['m', 'Min', 'Minor', 'min', 'minor']
    # Construct regular expression for matching key
    pattern = re.compile(
        # Start with any of A-G, a-g
        '^(?P<key>[ABCDEFGabcdefg])'
        # Next, look for #, b, or nothing
        '(?P<flatsharp>[#b]?)'
        # Allow for a space between key and mode
        ' ?'
        # Next, look for any of the mode strings
        '(?P<mode>(?:(?:' +
        # Next, look for any of the major or minor mode strings
        ')|(?:'.join(major_strs + minor_strs) + '))?)$')
    # Match provided key string
    result = re.match(pattern, key_string)
    if result is None:
        raise ValueError('Supplied key {} is not valid.'.format(key_string))
    # Convert result to dictionary
    result = result.groupdict()

    # Map from key string to pitch class number
    key_number = {'c': 0, 'd': 2, 'e': 4, 'f': 5,
                  'g': 7, 'a': 9, 'b': 11}[result['key'].lower()]
    # Increment or decrement pitch class if a flat or sharp was specified
    if result['flatsharp']:
        if result['flatsharp'] == '#':
            key_number += 1
        elif result['flatsharp'] == 'b':
            key_number -= 1
    # Circle around 12 pitch classes
    key_number = key_number % 12
    # Offset if mode is minor, or the key name is lowercase
    if result['mode'] in minor_strs or (result['key'].islower() and
                                        result['mode'] not in major_strs):
        key_number += 12

    return key_number