#!/usr/bin/python3 python

"""Testing that a MIDI loaded and saved unchanged is indeed the save as before.

"""

import shutil
from pathlib import Path

from tqdm import tqdm

from miditoolkit import MidiFile


def test_load_dump():
    midi_paths = list(Path("tests", "testcases").glob("**/*.mid"))
    out_path = Path("tests", "tmp", "load_dump")
    out_path.mkdir(parents=True, exist_ok=True)

    for path in tqdm(midi_paths, desc="Checking midis load/save"):
        midi = MidiFile(path)
        # Writing it unchanged
        midi.dump(out_path / path.name)
        # Loading it back
        midi2 = MidiFile(out_path / path.name)

        # Sorting the notes, as after dump the order might have changed
        for track1, track2 in zip(midi.instruments, midi2.instruments):
            track1.notes.sort(key=lambda x: (x.start, x.pitch, x.end, x.velocity))
            track2.notes.sort(key=lambda x: (x.start, x.pitch, x.end, x.velocity))

        assert midi == midi2

    # deletes tmp directory after tests
    shutil.rmtree(out_path)


if __name__ == "__main__":
    test_load_dump()
