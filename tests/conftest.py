import pytest


@pytest.fixture()
def disable_mido_checks(monkeypatch):
    """
    Disable internal checks in `mido`, for performance.
    """
    from mido.messages import messages

    monkeypatch.setattr(messages, "check_msgdict", lambda d: d)


@pytest.fixture()
def disable_mido_merge_tracks(monkeypatch):
    """
    Disallow `mido` from creating `merged_tracks` when files are loaded.

    We don't need `merged_tracks` in our tests, and it's slow to create.

    See https://github.com/mido/mido/pull/565.
    TODO: this could maybe be removed after the
          abovementioned PR is in a `mido` release.
    """
    from mido.midifiles import midifiles

    monkeypatch.setattr(midifiles, "merge_tracks", lambda tracks: None)
