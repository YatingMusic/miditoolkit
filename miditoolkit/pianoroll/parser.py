from copy import deepcopy
from typing import List, Tuple, Callable, Union

import numpy as np
from miditoolkit import Note
from miditoolkit.constants import PITCH_RANGE


def notes2pianoroll(
    notes: List[Note],
    pitch_range: Tuple[int, int] = None,
    pitch_offset: int = 0,
    resample_factor: float = 1.0,
    resample_method: Callable = round,
    velocity_threshold: int = 0,
    time_portion: Tuple[int, int] = None,
    keep_note_with_zero_duration: bool = True,
) -> np.ndarray:
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
        assert (
            def_low_pitch <= low_pitch < high_pitch <= def_high_pitch
        ), f"The pitch range must be comprise between {def_low_pitch} and {def_high_pitch} (included)."
        low_pitch = max(def_low_pitch, low_pitch - pitch_offset)
        high_pitch = min(def_high_pitch, high_pitch + pitch_offset)
    else:
        low_pitch, high_pitch = def_low_pitch, def_high_pitch

    # Resampling time
    if resample_factor != 1.0:
        max_tick = int(resample_method(max_tick * resample_factor))
        for note in note_stream:
            note.start = int(resample_method(note.start * resample_factor))
            note.end = int(resample_method(note.end * resample_factor))

    # Create pianoroll
    pianoroll = np.zeros(shape=(max_tick, high_pitch), dtype=np.int8)
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
            note.pitch < low_pitch or note.pitch > high_pitch
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
        resample_factor: float = 1.0,
        pitch_range: Union[int, Tuple[int, int]] = None,
):
    # Handles pitch range
    # Pads the pianoroll array so that the pitch dimension size is PITCH_RANGE[1] (128)
    if isinstance(pitch_range, int):
        low_pitch = pitch_range
    elif isinstance(pitch_range, tuple):
        low_pitch = pitch_range[0]
    else:
        low_pitch = PITCH_RANGE[0]
    high_pitch = low_pitch + pianoroll.shape[1]
    arrays = []
    if low_pitch != PITCH_RANGE[0]:
        arrays.append(np.zeros((pianoroll.shape[0], low_pitch), dtype=pianoroll.dtype))
    arrays.append(pianoroll)
    if high_pitch != PITCH_RANGE[1]:
        arrays.append(np.zeros((pianoroll.shape[0], PITCH_RANGE[1] - high_pitch), dtype=pianoroll.dtype))
    if len(arrays) > 1:
        pianoroll = np.concatenate(arrays, axis=1)

    # pad with zeros for the first and last events
    padded = np.pad(pianoroll, ((1, 1), (0, 0)), "constant")
    diff = np.diff(padded, axis=0)

    pitches, note_ons = np.nonzero((diff > 0).T)
    note_offs = np.nonzero((diff < 0).T)[1]

    notes = []
    for idx, pitch in enumerate(pitches):
        st = note_ons[idx]
        ed = note_offs[idx]
        velocity = pianoroll[st, pitch]
        velocity = max(0, min(127, velocity))
        notes.append(
            Note(
                velocity=int(velocity),
                pitch=pitch,
                start=int(st * resample_factor),
                end=int(ed * resample_factor),
            )
        )
    notes.sort(key=lambda x: x.start)
    return notes
