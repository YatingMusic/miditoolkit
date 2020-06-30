import os


def example_midi_file():
    # like librosa.util.example_audio_file()
    path_curfile = os.path.dirname(os.path.abspath(__file__))
    path_midi = os.path.join(path_curfile, 'examples', '1390.mid')
    return path_midi
