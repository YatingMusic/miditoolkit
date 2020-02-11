import numpy as np


def downsample(pianoroll, ori_resol, factor):
    pass


def tochroma(pianoroll):
    chroma = np.zeros((pianoroll.shape[0], 12))
    for note in range(12):
        chroma[:, note] = np.sum(pianoroll[:, note::12], axis=1)
    return chroma


def pitch_padding(pianoroll, pitch_range, padding_range=(0, 127), value=0):
    st, ed = pitch_range
    st_pad, ed_pad = padding_range
    res = np.pad(
        pianoroll,
        [(0, 0), (st - st_pad, ed_pad - ed + 1)],
        mode='constant',
        constant_values=value)
    return res


def normalize(tensor):
    res = (tensor - np.min(tensor)) / (np.max(tensor) - np.min(tensor))
    return res
