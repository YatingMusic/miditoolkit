# Miditoolkit

A Python package for working with MIDI files.

[![PyPI version fury.io](https://badge.fury.io/py/miditoolkit.svg)](https://pypi.python.org/pypi/miditoolkit/)
[![Python 3.7](https://img.shields.io/badge/python-3.7+-blue.svg)](https://www.python.org/downloads/release/)
[![GitHub CI](https://github.com/YatingMusic/miditoolkit/actions/workflows/pytest.yml/badge.svg)](https://github.com/YatingMusic/miditoolkit/actions/workflows/pytest.yml)
[![GitHub license](https://img.shields.io/github/license/YatingMusic/miditoolkit.svg)](https://github.com/YatingMusic/miditoolkit/blob/main/LICENSE)
[![Downloads](https://static.pepy.tech/badge/miditoolkit)](https://pepy.tech/project/miditoolkit)
[![Code style](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

Miditoolkit works by loading/writing MIDIs with [mido](https://github.com/mido/mido) in a user-friendly way. It is inspired from [pretty_midi](https://github.com/craffel/pretty-midi), with similar usage and core features, but handles the MIDI events in native **[ticks](https://www.recordingblogs.com/wiki/midi-tick)** time unit instead of seconds. It also comes with a few optimizations and speed-ups, and can parse MIDI tracks into **piano-rolls** for computation or visualization purposes.
If you are working with seconds time units (for e.g. music transcription), you'll be likely better with pretty_midi. Otherwise, if you are working solely on MIDI and symbolic music, miditoolkit should provide slightly faster performances.

## Main Features

* MIDI
    * Global
        * ticks per beat
        * tempo changes
        * key signatures
        * time signatures
        * lyrics
        * markers
    * Instruments
        * control changes
        * pitch bend
    * Editing
        * chunk/cropping
    * IO
        * BytesIO
* Piano-rolls
    * Tools
        * notes to piano-rolls
        * piano-rolls to notes
        * chromagram
    * Visualization
* External Library
   * [structure analysis](https://github.com/wayne391/sf_segmenter)

## TODO

* better documentation;
* finish the code cleaning of the pianoroll methods (vis);
* a way to switch the time in seconds across the whole MidiFile object;
* cropping Control Changes and bars;
* symbolic features
* new structural analysis

## Installation

You can install miditoolkit via [PYPI](https://pypi.org/project/miditoolkit/):

```bash
pip install miditoolkit
```

... or directly from git if you want to get the latest features or fixes (only recommended if you need it):

```bash
pip install git+https://github.com/YatingMusic/miditoolkit
```

## Example Usage

```python
from miditoolkit import MidiFile
from miditoolkit.midi.utils import example_midi_file

path_midi = example_midi_file()
midi_obj = MidiFile(path_midi)

print(midi_obj)
```

Output:

```
ticks per beat: 480
max tick: 72002
tempo changes: 68
time sig: 2
key sig: 0
markers: 71
lyrics: False
instruments: 2
```

A. [Parse and create MIDI files](examples/parse_and_create_MIDI_files.ipynb)
B. [Piano-roll Manipulation](examples/pinoroll_manipulation.ipynb)

## Philosophy

* [mido](https://github.com/mido/mido) processes MIDI files in the lower level such as messages and ports, and is the backend pretty_midi and miditoolkit;
* [pretty_midi](https://github.com/craffel/pretty-midi) parses MIDI files and pianorolls in seconds time unit, plus has audio related features;
* [pypianoroll](https://github.com/salu133445/pypianoroll) parses MIDI files into pianorolls in ticks time unit.

**Miditoolkit** is designed for handling MIDI in **[ticks](https://www.recordingblogs.com/wiki/midi-tick)**, the native time unit of the MIDI protocol. We keep the midi parser as simple as possible, and offer several important functions to complete the versatility. For example, piano-rolls, tick-to-second, chromagram, etc.
