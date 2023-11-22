from copy import deepcopy
from typing import Callable, List, Optional, Tuple, Union

import numpy as np

from miditoolkit import Note
from miditoolkit.constants import PITCH_RANGE


def notes2pianoroll(
    notes: List[Note],
    pitch_range: Optional[Tuple[int, int]] = None,
    pitch_offset: int = 0,
    resample_factor: Optional[float] = None,
    resample_method: Callable = round,
    velocity_threshold: int = 0,
    time_portion: Optional[Tuple[int, int]] = None,
    keep_note_with_zero_duration: bool = True,
) -> np.ndarray:
    r"""Converts a sequence of notes into a pianoroll numpy array.

    Args:
        notes: List of notes to convert.
        pitch_range: a range of pitch to cover. Notes outside of this range will be discarded. If not given,
            the method will represent all notes (pitches 0 to 127). (default: None)
        pitch_offset: an offset to pad the pianoroll up and down on the pitch dimension. (default: 0)
        resample_factor: factor to resample the time dimension. (default: None)
        resample_method: resampling method. (default: round)
        velocity_threshold: a threshold for the velocity of the notes. Notes with velocities below this
            threshold will be discarded. (default: 0)
        time_portion: time portion in tick to represent. (default: None)
        keep_note_with_zero_duration: option to keep the notes with a duration of 0 ticks, by
            representing them with a duration of 1 tick.

    Returns: the pianoroll as a numpy array of two dimensions: the first is the time, the second is the pitch.

    """
    # Checks
    assert len(notes) > 0, "No notes were provided, at list one must be in the list."
    assert (
        0 <= velocity_threshold <= 127
    ), "The velocity threshold must be comprised between 0 and 127 (included)."
    assert (
        0 <= pitch_offset < 127
    ), "The pitch offset must be comprised between 0 and 126 (included)."

    # Copy and sort the notes
    note_stream = deepcopy(notes)
    note_stream.sort(key=lambda x: (x.end, x.start, x.velocity))

    # Set start and end tick
    if time_portion is not None:
        start_tick, max_tick = time_portion
    else:
        start_tick = 0
        max_tick = note_stream[-1].end

    # Pitch range detection
    def_low_pitch, def_high_pitch = PITCH_RANGE
    if pitch_range is not None:
        low_pitch, high_pitch = pitch_range
        low_pitch = max(def_low_pitch, low_pitch - pitch_offset)
        high_pitch = min(def_high_pitch, high_pitch + pitch_offset)
    else:
        low_pitch, high_pitch = def_low_pitch, def_high_pitch

    # Resampling time
    if resample_factor is not None:
        max_tick = int(resample_method(max_tick * resample_factor))
        for note in note_stream:
            note.start = int(resample_method(note.start * resample_factor))
            note.end = int(resample_method(note.end * resample_factor))

    # Create pianoroll
    pianoroll = np.zeros(shape=(max_tick, high_pitch + 1), dtype=np.int8)
    for note in note_stream:
        # Discarding notes having velocity under the threshold
        # Or outside the tick portion, or the pitch range
        if note.velocity < velocity_threshold:
            continue
        if note.end < start_tick:
            continue
        if note.start > max_tick:
            break
        if pitch_range is not None and (
            note.pitch < pitch_range[0] or note.pitch > pitch_range[1]
        ):
            continue

        # Adjust notes times if needed
        if note.start < start_tick:
            note.start = start_tick
        if note.end > max_tick:
            note.end = max_tick

        # keep notes with zero length (set to 1)
        if keep_note_with_zero_duration and note.start == note.end:
            note.end += 1

        # set array value
        indices = (
            list(range(note.start, note.end)),
            [note.pitch] * (note.end - note.start),
        )
        pianoroll[indices] = note.velocity

    # Cut the array if needed on its two dimensions (time, pitch)
    if start_tick > 0:
        pianoroll = pianoroll[start_tick:]
    if pitch_range is None:
        # Automatically cut the lowest and highest
        pitch_played = np.where(np.any(pianoroll != 0, axis=0) == 1)[0]
        low_pitch = max(def_low_pitch, pitch_played[0] - pitch_offset)
        high_pitch = min(def_high_pitch, pitch_played[-1] - def_high_pitch)
    if low_pitch != def_low_pitch or high_pitch != def_high_pitch:
        pianoroll = pianoroll[:, low_pitch : high_pitch + 1]

    return pianoroll


def pianoroll2notes(
    pianoroll: np.ndarray,
    resample_factor: Optional[float] = None,
    pitch_range: Optional[Union[int, Tuple[int, int]]] = None,
) -> List[Note]:
    """Converts a pianoroll (numpy array) into a sequence of notes.

    Args:
        pianoroll: pianoroll to convert.
        resample_factor: factor to resample the time dimension. (default: None)
        pitch_range: a range of pitch to cover. Notes outside of this range will be discarded. If not given,
            the method will represent all notes (pitches 0 to 127). (default: None)

    Returns: sequence of notes.

    """
    # Handles pitch range
    # Pads the pianoroll array so that the pitch dimension size is PITCH_RANGE[1] (128)
    if isinstance(pitch_range, int):
        low_pitch = pitch_range
        high_pitch = low_pitch + pianoroll.shape[1]
    elif isinstance(pitch_range, tuple):
        low_pitch, high_pitch = pitch_range
    else:
        low_pitch = PITCH_RANGE[0]
        high_pitch = low_pitch + pianoroll.shape[1]
    arrays = []
    if low_pitch != PITCH_RANGE[0]:
        arrays.append(np.zeros((pianoroll.shape[0], low_pitch), dtype=pianoroll.dtype))
    arrays.append(pianoroll)
    if high_pitch != PITCH_RANGE[1]:
        arrays.append(
            np.zeros(
                (pianoroll.shape[0], PITCH_RANGE[1] - high_pitch), dtype=pianoroll.dtype
            )
        )
    if len(arrays) > 1:
        pianoroll = np.concatenate(arrays, axis=1)

    # pad with zeros for the first and last events
    padded = np.pad(pianoroll > 0, ((1, 1), (0, 0)), "constant")
    diff = np.diff(padded.astype(np.int8), axis=0)

    pitches, note_ons = np.nonzero((diff > 0).T)
    note_offs = np.nonzero((diff < 0).T)[1]

    notes = []
    for idx, pitch in enumerate(pitches):
        st = note_ons[idx]
        ed = note_offs[idx]
        velocity = int(pianoroll[st, pitch])
        velocity = max(0, min(127, velocity))
        if resample_factor is not None:
            st, ed = int(st * resample_factor), int(ed * resample_factor)
        notes.append(
            Note(
                velocity=int(velocity),
                pitch=pitch,
                start=st,
                end=ed,
            )
        )
    notes.sort(key=lambda x: x.start)
    return notes
