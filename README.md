# miditoolkit

A python package for working with MIDI data. 

The usage is similar to [pretty_midi](https://github.com/craffel/pretty-midi), while this toolkit handling midi events in [symbolic timing](https://mido.readthedocs.io/en/latest/midi_files.html#about-the-time-attribute) (**ticks**, instead of seconds). Furthermore, the toolkit can parse midi tracks into **piano-rolls** for computation or visualization purposes.

## Main Features
* midi events
    * global
        * ticks per beats
        * tempo changes
        * key signatures
        * time signature
        * lyrics
        * makers
    * instruments
        * control changes
        * pitch bend
* piano-rolls    
    * tools
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

```

### Ceate an empty MIDI File

## Visualization

## Philosophy