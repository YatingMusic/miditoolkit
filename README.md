# miditoolkit

A python package for working with MIDI data. 

The usage is similar to [pretty_midi](https://github.com/craffel/pretty-midi), while miditoolkit handles MIDI events in [symbolic timing](https://mido.readthedocs.io/en/latest/midi_files.html#about-the-time-attribute) (**ticks**, instead of seconds). Furthermore, the toolkit can parse MIDI  tracks into **piano-rolls** for computation or visualization purposes.

## Main Features
* MIDI attributes
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

A. Parse a MIDI file  
B. Ceate an empty MIDI File  
C. Create a piano-roll and visualize it  

### A. Parse a MIDI file
```python
from miditoolkit.midi import parser as mid_parser  

# load midi file
path_midi = '../testcases/2.midi'
mido_obj = mid_parser.MidiFile(path_midi)

# ticks per beats
print(' > ticks per beat:', mido_obj.ticks_per_beat)

# signatures
print('\n -- time signatures -- ')
print(' > amount:', len(mido_obj.time_signature_changes))
print(mido_obj.time_signature_changes[0])

print('\n -- key signatures --')
print(' > amount:', len(mido_obj.key_signature_changes))

# tempo changes
print('\n -- tempo changes --')
print(' > amount:', len(mido_obj.tempo_changes))
print(mido_obj.tempo_changes[0])

# markers
print('\n -- markers --')
print(' > amount:', len(mido_obj.markers))
print(mido_obj.markers[0])

# instruments
print('\n -- instruments --')
print(' > number of tracks:', len(mido_obj.instruments))
print(' > number of notes:', len(mido_obj.instruments[0].notes))

# convert to seconds
note = mido_obj.instruments[0].notes[20]
mapping = mido_obj.get_tick_to_time_mapping()
tick = note.start
sec = mapping[tick]
print('{} tick at {} seconds'.format(tick, sec))
```

```bash
 > ticks per beat: 480

 -- time signatures -- 
 > amount: 1
4/4 at 0 ticks

 -- key signatures --
 > amount: 0

 -- tempo changes --
 > amount: 257
85.00004250002125 BPM at 0 ticks

 -- markers --
 > amount: 79
"C#:maj" at 0 ticks

 -- instruments --
 > number of tracks: 1
 > number of notes: 748
3840 tick at 5.535648999999999 seconds
```

### B. Ceate an empty MIDI file
```python
from miditoolkit.midi import parser as mid_parser 
from miditoolkit.midi import containers as ct

midi_obj = mid_parser.MidiFile()


```

```bash

```

### C. Create a piano-roll
```python
from miditoolkit.midi import parser as mid_parser 
from miditoolkit.pianoroll import parser as pr_parser 


```

### D. Crop MIDI segment
```python

```

## Visualization

```python
```

## Philosophy
* [pretty_midi](https://github.com/craffel/pretty-midi) can parse MIDI files and generate pianorolls in absolute timing (seconds). 
* [pypianoroll](https://github.com/salu133445/pypianoroll) can parse MIDI files into pianorolls in symbolic timing (through beat resolution).
* [mido](https://github.com/mido/mido) processes MIDI files in the lower level such as messages and ports.

**Miditoolkit** is designed for handling MIDI in **symbolic timing** (ticks), which is the native format of MIDI timing. We keep the midi parser as simple as possible, and offer several important functions to complete the versatility. For example, piano-rolls, tick-to-second, chromagram, and etc.

To customize settings and maximum the degree of freedom, users can use additional libraries like visualization, which are excluded in the toolkit. 


