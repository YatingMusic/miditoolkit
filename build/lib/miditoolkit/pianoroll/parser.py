import numpy as np
from copy import deepcopy
from scipy.sparse import csc_matrix
import miditoolkit.midi.containers as ct


PITCH_RANGE = 128


# def get_onsets_pianoroll():
#     pass


# def get_offsets_pianoroll():
#     pass


def notes2pianoroll(
        note_stream_ori, 
        ticks_per_beat=480, 
        downbeat=None, 
        resample_factor=1.0, 
        resample_method=round,
        binary_thres=None,
        max_tick=None,
        to_sparse=False, 
        keep_note=True):
    
    # pass by value
    note_stream = deepcopy(note_stream_ori)

    # sort by end time
    note_stream = sorted(note_stream, key=lambda x: x.end)
    
    # set max tick
    if max_tick is None:
        max_tick = 0 if len(note_stream) == 0 else note_stream[-1].end
        
    # resampling
    if resample_factor != 1.0:
        max_tick = int(resample_method(max_tick * resample_factor))
        for note in note_stream:
            note.start = int(resample_method(note.start * resample_factor))
            note.end = int(resample_method(note.end * resample_factor))
    
    # create pianoroll
    time_coo = []
    pitch_coo = []
    velocity = []
    
    for note in note_stream:
        # discard notes having no velocity
        if note.velocity == 0:
            continue

        # duration
        duration = note.end - note.start

        # keep notes with zero length (set to 1)
        if keep_note and (duration == 0):
            duration = 1
            note.end += 1

        # set time
        time_coo.extend(np.arange(note.start, note.end))
        
        # set pitch
        pitch_coo.extend([note.pitch] * duration)
        
        # set velocity
        v_tmp = note.velocity
        if binary_thres is not None:
            v_tmp = v_tmp > binary_thres
        velocity.extend([v_tmp] * duration)
    
    # output
    pianoroll = csc_matrix((velocity, (time_coo, pitch_coo)), shape=(max_tick, PITCH_RANGE))
    pianoroll = pianoroll if to_sparse else pianoroll.toarray()
    
    return pianoroll      


def pianoroll2notes(
        pianoroll,
        resample_factor=1.0):

    binarized = pianoroll > 0
    padded = np.pad(binarized, ((1, 1), (0, 0)), "constant")
    diff = np.diff(padded.astype(np.int8), axis=0)

    positives = np.nonzero((diff > 0).T)
    pitches = positives[0]
    note_ons = positives[1]
    note_offs = np.nonzero((diff < 0).T)[1]

    notes = []
    for idx, pitch in enumerate(pitches):
        st = note_ons[idx] 
        ed = note_offs[idx]
        velocity = pianoroll[st, pitch]
        velocity = max(0, min(127, velocity))
        notes.append(
            ct.Note(
                velocity=int(velocity), 
                pitch=pitch, 
                start=int(st*resample_factor), 
                end=int(ed*resample_factor)))
    notes.sort(key=lambda x: x.start)
    return notes