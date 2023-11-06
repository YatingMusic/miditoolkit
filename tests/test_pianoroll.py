#!/usr/bin/python3 python

"""Testing creating pianorolls of notes.

"""

from pathlib import Path

from miditoolkit import MidiFile, notes2pianoroll, pianoroll2notes
from tqdm import tqdm


def test_pianoroll():
    midi_paths = list(Path("tests", "testcases").glob("**/*.mid"))
    # TODO several sets of test params
    test_tests = [
        {},
        {"pitch_range": (24, 96)},
    ]

    for path in tqdm(midi_paths, desc="Checking pianoroll conversion"):
        midi = MidiFile(path)

        for track in midi.instruments:
            # We do a first notes -> pianoroll -> notes conversion before
            # This step is required as the pianoroll conversion is lossy with overlapping notes.
            # notes2pianoroll has a "last income priority" logic, for which if a notes is occurs
            # when another one of the same pitch is already being played, this new note will be
            # represented and will end the previous one (if they have different velocities).
            # deduplicate_notes(track.notes)

            # First pianoroll <--> notes conversion, losing overlapping notes
            pianoroll = notes2pianoroll(track.notes)
            new_notes = pianoroll2notes(pianoroll)

            # Second one, notes -> pianoroll -> new notes should be equal
            new_pianoroll = notes2pianoroll(new_notes)
            new_new_notes = pianoroll2notes(new_pianoroll)

            # Assert notes are all retrieved
            assert len(new_notes) == len(
                new_new_notes
            ), "Number of notes changed in pianoroll conversion"
            for note1, note2 in zip(new_notes, new_new_notes):
                assert (
                    note1 == note2
                ), "Notes before and after pianoroll conversion are not the same"


if __name__ == "__main__":
    test_pianoroll()
