# miditoolkit

A python package for working with MIDI data. 

The usage is similar to [pretty_midi](https://github.com/craffel/pretty-midi), while miditoolkit handles MIDI events in [symbolic timing](https://mido.readthedocs.io/en/latest/midi_files.html#about-the-time-attribute) (**ticks**, instead of seconds). Furthermore, the toolkit can parse MIDI  tracks into **piano-rolls** for computation or visualization purposes.

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
        * cropping
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

## Installation
* current version: 0.1.14
* **python 2 is not supported**   
* Install the miditoolkit via [PYPI](https://pypi.org/project/miditoolkit/):
```bash
pip install miditoolkit
```

## Example Usage

```python
import miditoolkit
path_midi = miditoolkit.midi.utils.example_midi_file()
midi_obj = miditoolkit.midi.parser.MidiFile(path_midi)
print(midi_obj)

"""
Output:

ticks per beat: 480
max tick: 72002
tempo changes: 68
time sig: 2
key sig: 0
markers: 71
lyrics: False
instruments: 2

"""
```
A. [Parse and create MIDI files](examples/parse_and_create_MIDI_files.ipynb)  
B. [Piano-roll Manipulation](examples/pinoroll_manipulation.ipynb)


## Philosophy
* [pretty_midi](https://github.com/craffel/pretty-midi) can parse MIDI files and generate pianorolls in absolute timing (seconds). 
* [pypianoroll](https://github.com/salu133445/pypianoroll) can parse MIDI files into pianorolls in symbolic timing (through beat resolution).
* [mido](https://github.com/mido/mido) processes MIDI files in the lower level such as messages and ports.

**Miditoolkit** is designed for handling MIDI in **symbolic timing** (ticks), which is the native format of MIDI timing. We keep the midi parser as simple as possible, and offer several important functions to complete the versatility. For example, piano-rolls, tick-to-second, chromagram, and etc.

To customize settings and maximum the degree of freedom, users can use additional libraries like visualization, which are excluded in the toolkit. 


