import miditoolkit


path_midi = miditoolkit.midi.utils.example_midi_file()
midi_obj = miditoolkit.midi.parser.MidiFile(path_midi)

print(midi_obj)