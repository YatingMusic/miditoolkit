#!/usr/bin/python3 python
from operator import attrgetter

import pytest

from miditoolkit import MidiFile
from miditoolkit.constants import PITCH_RANGE
from miditoolkit.pianoroll import notes2pianoroll, pianoroll2notes
from tests.utils import MIDI_PATHS

test_sets = [
    {"pitch_range": (0, 127)},
    {"pitch_range": (24, 96)},
    {"pitch_range": (24, 116), "pitch_offset": 12},
    {"pitch_range": (6, 96), "pitch_offset": 12},
    {"pitch_range": (24, 96), "pitch_offset": 12, "velocity_threshold": 36},
]


@pytest.mark.parametrize("midi_path", MIDI_PATHS, ids=attrgetter("name"))
@pytest.mark.parametrize("test_set", test_sets)
def test_pianoroll(midi_path, test_set, disable_mido_checks, disable_mido_merge_tracks):
    """Testing creating pianorolls of notes."""

    # Set pitch range parameters
    pitch_range = test_set.get("pitch_range", PITCH_RANGE)
    if "pitch_offset" in test_set:
        pitch_range = (
            max(PITCH_RANGE[0], pitch_range[0] - test_set["pitch_offset"]),
            min(PITCH_RANGE[1], pitch_range[1] + test_set["pitch_offset"]),
        )

    midi = MidiFile(midi_path)

    for track in midi.instruments:
        # We do a first notes -> pianoroll -> notes conversion before
        # This step is required as the pianoroll conversion is lossy with overlapping notes.
        # notes2pianoroll has a "last income priority" logic, for which if a notes is occurs
        # when another one of the same pitch is already being played, this new note will be
        # represented and will end the previous one (if they have different velocities).

        # First pianoroll <--> notes conversion, losing overlapping notes
        pianoroll = notes2pianoroll(track.notes, **test_set)
        new_notes = pianoroll2notes(pianoroll, pitch_range=pitch_range)

        # Second one, notes -> pianoroll -> new notes should be equal
        new_pianoroll = notes2pianoroll(new_notes, **test_set)
        new_new_notes = pianoroll2notes(new_pianoroll, pitch_range=pitch_range)
        if "velocity_threshold" in test_set:
            new_notes = [
                note
                for note in new_notes
                if note.velocity >= test_set["velocity_threshold"]
            ]

        # Assert notes are all retrieved
        assert len(new_notes) == len(
            new_new_notes
        ), "Number of notes changed in pianoroll conversion"
        for note1, note2 in zip(new_notes, new_new_notes):
            # We don't test the resampling factor as it might later the number of notes
            assert (
                note1 == note2
            ), "Notes before and after pianoroll conversion are not the same"
