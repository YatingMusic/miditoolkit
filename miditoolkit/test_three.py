from miditoolkit.midi import parser as mid_parser  
import pretty_midi as pm
import mido

# testcase
path_midi = 'groove/drummer1/eval_session/1_funk-groove1_138_beat_4-4.mid'
 
# load                                   
mt_obj = mid_parser.MidiFile(path_midi)
pm_obj = pm.PrettyMIDI(path_midi)
mido_obj = mido.MidiFile(path_midi)

# check
print('pretty-midi:', len(pm_obj.instruments[0].notes))
print('miditoolkit:', len(mt_obj.instruments[0].notes))

# mido msg
cnt_note_on = 0
cnt_note_off = 0
note_ons = []
note_offs = []
for msg in mido_obj:
    if msg.type == 'note_on' :
        if msg.velocity == 0:
            note_offs.append(msg)
        else:
            note_ons.append(msg)
    if msg.type == 'note_off':
        note_offs.append(msg)

# check
print(' cnt_note_on:', len(note_ons))
print('cnt_note_off:', len(note_offs))