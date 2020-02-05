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


