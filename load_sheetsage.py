from mido import MidiFile
import miditoolkit

# mid = MidiFile('/Users/poshuncheng/Downloads/rAyAZcva3AY (1).mid')

# for i, track in enumerate(mid.tracks):
#     msgs = [msg for msg in track]
#     print('Track {}: {}'.format(i, track.name), len( msgs ))
#     #
#     #     print(msg)


# for msg in mid.tracks[0]:
#     print(msg)

import miditoolkit

path_midi = '/Users/poshuncheng/Downloads/rAyAZcva3AY (1).mid'
midi_obj = miditoolkit.midi.parser.MidiFile(path_midi)
print(midi_obj)

for l in midi_obj.lyrics:
    print(l)