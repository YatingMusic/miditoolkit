from operator import attrgetter

import pytest

from miditoolkit import MidiFile
from tests.utils import MIDI_PATHS


@pytest.mark.parametrize("midi_path", MIDI_PATHS, ids=attrgetter("name"))
def test_load_dump(midi_path, tmp_path, disable_mido_checks, disable_mido_merge_tracks):
    """Test that a MIDI loaded and saved unchanged is indeed the save as before."""
    midi1 = MidiFile(midi_path)
    dump_path = tmp_path / midi_path.name
    midi1.dump(dump_path)  # Writing it unchanged
    midi2 = MidiFile(dump_path)  # Loading it back

    # Sorting the notes, as after dump the order might have changed
    for track1, track2 in zip(midi1.instruments, midi2.instruments):
        track1.notes.sort(key=lambda x: (x.start, x.pitch, x.end, x.velocity))
        track2.notes.sort(key=lambda x: (x.start, x.pitch, x.end, x.velocity))

    assert midi1 == midi2
