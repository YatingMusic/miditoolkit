#!/usr/bin/python3 python

"""Testing that a MIDI loaded and saved unchanged is indeed the save as before.

"""

from pathlib import Path

from miditoolkit import MidiFile
from tqdm import tqdm


def test_load_dump():
    midi_paths = list(Path("tests", "test_cases").glob("**/*.mid"))
    for path in tqdm(midi_paths, desc="Checking midis load/save"):
        midi = MidiFile(path)
        # Writing it unchanged
        midi.dump(path.name)
        # Loading it back
        midi2 = MidiFile(path.name)

        # Sorting the notes, as after dump the order might have changed
        for track1, track2 in zip(midi.instruments, midi2.instruments):
            track1.notes.sort(key=lambda x: (x.start, x.pitch, x.end, x.velocity))
            track2.notes.sort(key=lambda x: (x.start, x.pitch, x.end, x.velocity))

        assert midi == midi2


if __name__ == "__main__":
    test_merge_tracks()
