from operator import attrgetter

import pytest

from miditoolkit import MidiFile, Note
from tests.utils import MIDI_PATHS


@pytest.mark.parametrize("midi_path", MIDI_PATHS[:5], ids=attrgetter("name"))
def test_remove_notes_with_no_duration(
    midi_path, tmp_path, disable_mido_checks, disable_mido_merge_tracks
):
    """Test that a MIDI loaded and saved unchanged is indeed the save as before."""
    # Load the MIDI file and removes the notes with durations <= 0
    midi = MidiFile(midi_path)
    midi.instruments[0].remove_notes_with_no_duration()
    num_notes_before = midi.instruments[0].num_notes

    # Adding notes with durations <= 0, then reapply the method
    midi.instruments[0].notes.append(Note(50, 50, 100, 100))
    midi.instruments[0].notes.append(Note(50, 50, 101, 100))
    midi.instruments[0].remove_notes_with_no_duration()

    assert (
        midi.instruments[0].num_notes == num_notes_before
    ), "The notes with duration <=0 were not removed by test_remove_notes_with_no_duration"
