# miditoolkit

A python package for working with MIDI data. 

The usage is similar to [pretty_midi](https://github.com/craffel/pretty-midi), while this toolkit handles MIDI events in [symbolic timing](https://mido.readthedocs.io/en/latest/midi_files.html#about-the-time-attribute) (**ticks**, instead of seconds). Furthermore, the toolkit can parse MIDI  tracks into **piano-rolls** for computation or visualization purposes.

## Main Features
* MIDI attributes
    * Global
        * ticks per beats
        * tempo changes
        * key signatures
        * time signatures
        * lyrics
        * makers
    * Instruments
        * control changes
        * pitch bend
* Piano-rolls    
    * Tools
        * notes to piano-rolls
        * piano-rolls to notes
        * chromagram
    * Visualization

## Installation
Install the miditoolkit via [PYPI](https://pypi.org/project/miditoolkit/):
```bash
pip install miditoolkit
```

## Quick Start
* Parse a MIDI file
* Ceate an empty MIDI File
* Create a piano-roll and visualize it

### Parse a MIDI file
```python

from miditoolkit.midi import parser as mid_parser 
from miditoolkit.pianoroll import parser as pr_parser 

# load midi file
path_midi = 'testcases/2.midi'
mido_obj = mid_parser.MidiFile(path_midi)

# ticks per beats
print(mido_obj.ticks_per_beat)

# signatures
print('time signatures:')
print(mido_obj.time_signature_changes)

print('time signatures:')
print(mido_obj.time_signature_changes)

# tempo changes

# markers

# instruments

# convert to seconds

```

### Ceate an empty MIDI File
```python
from miditoolkit.midi import parser as mid_parser 
from miditoolkit.midi import containers as ct

midi_obj = mid_parser.MidiFile()


```

### Create a piano-roll
```python
from miditoolkit.midi import parser as mid_parser 
from miditoolkit.pianoroll import parser as pr_parser 


```

## Visualization

```python
```

## Philosophy

* [pretty_midi](https://github.com/craffel/pretty-midi) can parse MIDI files and generate pianorolls in absolute timing (seconds).
* [pypianoroll](https://github.com/salu133445/pypianoroll) can parse MIDI files into pianorolls in symbolic timing (through beat resolution).
* [mido](https://github.com/mido/mido) process MIDI files in the lower level such as messages and ports.

Miditoolkit is designed for handling MIDI in **symbolic timing** (ticks), which is the native format of MIDI timing. We keep the midi parser as simple as possible, and offer several important functions to complete the versatility.

To customized settings and maximum the degree of freedom, users can achieve that by using additional libraries like visualization, which is excluded in the toolkit. 


