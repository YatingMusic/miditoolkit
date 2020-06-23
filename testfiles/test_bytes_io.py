import miditoolkit.midi.parser as mid_parser
from miditoolkit.midi import containers as ct

import numpy as np
from io import BytesIO


# -------------------------------------- #
#  Create dummy file                     #
# -------------------------------------- #
# create an empty file
mido_obj = mid_parser.MidiFile()
beat_resol = mido_obj.ticks_per_beat

# create an  instrument
track = ct.Instrument(program=0, is_drum=False, name='example track')
mido_obj.instruments = [track]

# create eighth notes
duration = int(beat_resol * 0.5)
prev_end = 0
pitch = 60
print(' > create a dummy file')
for i in range(10):
    # create one note
    start = prev_end
    end = prev_end + duration
    pitch = pitch
    velocity = np.random.randint(1, 127)
    note = ct.Note(start=start, end=end, pitch=pitch, velocity=velocity)
    print(i, note)
    mido_obj.instruments[0].notes.append(note)
    
    # prepare next
    prev_end = end
    pitch += 1

# save (with BytesIO)
memory = BytesIO()
mido_obj.dump(file=memory)

# -------------------------------------- #
#  Test Bytes IO                         #
# -------------------------------------- #
print(' === reload ===')
memory.seek(0)
mid_load = mid_parser.MidiFile(file=memory)
for idx, note in enumerate(mid_load.instruments[0].notes):
    print(idx, note)