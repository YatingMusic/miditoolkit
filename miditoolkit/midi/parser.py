import collections
import functools
from pathlib import Path
from typing import List, Optional, Sequence, Tuple, Union

import mido
import numpy as np

from ..constants import DEFAULT_BPM
from .containers import (
    ControlChange,
    Instrument,
    KeySignature,
    Lyric,
    Marker,
    Note,
    Pedal,
    PitchBend,
    TempoChange,
    TimeSignature,
)

# We "hack" mido's Note_on messages checks to allow to add an "end" attribute, that
# will serve us to sort the messages in the good order when writing a MIDI file.
new_set = {"end", *mido.messages.SPEC_BY_TYPE["note_on"]["attribute_names"]}
mido.messages.SPEC_BY_TYPE["note_on"]["attribute_names"] = new_set
mido.messages.checks._CHECKS["end"] = mido.messages.checks.check_time


class MidiFile:
    def __init__(
        self,
        filename: Optional[Union[Path, str]] = None,
        file=None,
        ticks_per_beat: int = 480,
        clip: bool = False,
        charset: str = "latin1",
    ):
        # create empty file
        self.ticks_per_beat: int = ticks_per_beat
        self.max_tick: int = 0
        self.tempo_changes: List[TempoChange] = []
        self.time_signature_changes: List[TimeSignature] = []
        self.key_signature_changes: List[KeySignature] = []
        self.lyrics: List[Lyric] = []
        self.markers: List[Marker] = []
        self.instruments: List[Instrument] = []

        # load file
        if filename or file:
            if filename:
                mido_obj = mido.MidiFile(filename=filename, clip=clip, charset=charset)
            else:
                mido_obj = mido.MidiFile(file=file, clip=clip, charset=charset)

            # ticks_per_beat
            self.ticks_per_beat = mido_obj.ticks_per_beat

            # convert delta time to cumulative time
            self._convert_delta_to_cumulative(mido_obj)

            # load tempo changes
            self.tempo_changes = self._load_tempo_changes(mido_obj)

            # load key signatures
            self.key_signature_changes = self._load_key_signatures(mido_obj)

            # load time signatures
            self.time_signature_changes = self._load_time_signatures(mido_obj)

            # load markers
            self.markers = self._load_markers(mido_obj)

            # load lyrics
            self.lyrics = self._load_lyrics(mido_obj)

            # sort events by time
            self.time_signature_changes.sort(key=lambda ts: ts.time)
            self.key_signature_changes.sort(key=lambda ks: ks.time)
            self.lyrics.sort(key=lambda lyc: lyc.time)

            # compute max tick
            self.max_tick = max([max([e.time for e in t]) for t in mido_obj.tracks]) + 1

            # load instruments
            self.instruments = self._load_instruments(mido_obj)

        # tick and sec mapping

    @staticmethod
    def _convert_delta_to_cumulative(mido_obj: mido.MidiFile):
        for track in mido_obj.tracks:
            tick = 0
            for event in track:
                event.time += tick
                tick = event.time

    @staticmethod
    def _load_tempo_changes(mido_obj: mido.MidiFile) -> List[TempoChange]:
        # default bpm
        tempo_changes = [TempoChange(DEFAULT_BPM, 0)]

        # traversing
        for track in mido_obj.tracks:
            for event in track:
                if event.type == "set_tempo":
                    # convert tempo to BPM
                    tempo = mido.tempo2bpm(event.tempo)
                    tick = event.time
                    if tick == 0:
                        tempo_changes = [TempoChange(tempo, 0)]
                    else:
                        last_tempo = tempo_changes[-1].tempo
                        if tempo != last_tempo:
                            tempo_changes.append(TempoChange(tempo, tick))
        return tempo_changes

    @staticmethod
    def _load_time_signatures(mido_obj: mido.MidiFile) -> List[TimeSignature]:
        # no default
        time_signature_changes = []

        # traversing
        for track in mido_obj.tracks:
            for event in track:
                if event.type == "time_signature":
                    ts_obj = TimeSignature(
                        event.numerator, event.denominator, event.time
                    )
                    time_signature_changes.append(ts_obj)
        return time_signature_changes

    @staticmethod
    def _load_key_signatures(mido_obj: mido.MidiFile) -> List[KeySignature]:
        # no default
        key_signature_changes = []

        # traversing
        for track in mido_obj.tracks:
            for event in track:
                if event.type == "key_signature":
                    key_obj = KeySignature(event.key, event.time)
                    key_signature_changes.append(key_obj)
        return key_signature_changes

    @staticmethod
    def _load_markers(mido_obj: mido.MidiFile) -> List[Marker]:
        # no default
        markers = []

        # traversing
        for track in mido_obj.tracks:
            for event in track:
                if event.type == "marker":
                    markers.append(Marker(event.text, event.time))
        return markers

    @staticmethod
    def _load_lyrics(mido_obj: mido.MidiFile) -> List[Lyric]:
        # no default
        lyrics = []

        # traversing
        for track in mido_obj.tracks:
            for event in track:
                if event.type == "lyrics":
                    lyrics.append(Lyric(event.text, event.time))
        return lyrics

    @staticmethod
    def _load_instruments(midi_data: mido.MidiFile) -> List[Instrument]:
        instrument_map = collections.OrderedDict()
        # Store a similar mapping to instruments storing "straggler events",
        # e.g. events which appear before we want to initialize an Instrument
        stragglers = {}
        # This dict will map track indices to any track names encountered
        track_name_map = collections.defaultdict(str)

        def __get_instrument(
            program_: int,
            channel: int,
            track_: int,
            create_new: bool,
        ):
            """Gets the Instrument corresponding to the given program number,
            drum/non-drum type, channel, and track index.  If no such
            instrument exists, one is created.

            """
            # If we have already created an instrument for this program
            # number/track/channel, return it
            if (program_, channel, track_) in instrument_map:
                return instrument_map[(program_, channel, track_)]
            # If there's a straggler instrument for this instrument and we
            # aren't being requested to create a new instrument
            if not create_new and (channel, track_) in stragglers:
                return stragglers[(channel, track_)]
            is_drum = channel == 9
            # If we are told to, create a new instrument and store it
            if create_new:
                instrument_ = Instrument(program_, is_drum, track_name_map[track_idx])
                # If any events appeared for this instrument before now,
                # include them in the new instrument
                if (channel, track_) in stragglers:
                    straggler = stragglers[(channel, track_)]
                    instrument_.control_changes = straggler.control_changes
                    instrument_.pitch_bends = straggler.pitch_bends
                    instrument_.pedals = straggler.pedals
                # Add the instrument to the instrument map
                instrument_map[(program_, channel, track_)] = instrument_
            # Otherwise, create a "straggler" instrument which holds events
            # which appear before we actually want to create a proper new
            # instrument
            else:
                # Create a "straggler" instrument
                instrument_ = Instrument(program_, is_drum, track_name_map[track_idx])
                # Note that stragglers ignores program number, because we want
                # to store all events on a track which appear before the first
                # note-on, regardless of program
                stragglers[(channel, track_)] = instrument_
            return instrument_

        for track_idx, track in enumerate(midi_data.tracks):
            # Keep track of last note on location:
            # key = (instrument, note), value = (note-on tick, velocity)
            last_note_on = collections.defaultdict(list)
            # Keep track of which instrument is playing in each channel
            # initialize to program 0 for all channels
            current_instrument = np.zeros(16, dtype=np.int8)
            ped_list = []
            for event in track:
                # Look for track name events
                if event.type == "track_name":
                    # Set the track name for the current track
                    track_name_map[track_idx] = event.name
                # Look for program change events
                if event.type == "program_change":
                    # Update the instrument for this channel
                    current_instrument[event.channel] = event.program
                # Note ons are note on events with velocity > 0
                elif event.type == "note_on" and event.velocity > 0:
                    # Store this as the last note-on location
                    note_on_index = (event.channel, event.note)
                    last_note_on[note_on_index].append((event.time, event.velocity))
                # Note offs can also be note on events with 0 velocity
                elif event.type == "note_off" or (
                    event.type == "note_on" and event.velocity == 0
                ):
                    # Check that a note-on exists (ignore spurious note-offs)
                    key = (event.channel, event.note)
                    if key in last_note_on:
                        # Get the start/stop times and velocity of every note
                        # which was turned on with this instrument/drum/pitch.
                        # Since mido makes (note on - note off) pair for a note,
                        # one note-off close one note-on in FIFO method.
                        end_tick = event.time
                        open_notes = last_note_on[key]

                        notes_to_close = [open_notes[0]]
                        notes_to_keep = [
                            (start_tick, velocity)
                            for start_tick, velocity in open_notes[1:]
                        ]

                        for start_tick, velocity in notes_to_close:
                            start_time = start_tick
                            end_time = end_tick
                            # Create the note event
                            note = Note(velocity, event.note, start_time, end_time)
                            # Get the program and drum type for the current
                            # instrument
                            program = current_instrument[event.channel]
                            # Retrieve the Instrument instance for the current
                            # instrument
                            # Create a new instrument if none exists
                            instrument = __get_instrument(
                                program, event.channel, track_idx, True
                            )
                            # Add the note event
                            instrument.notes.append(note)

                        if len(notes_to_close) > 0 and len(notes_to_keep) > 0:
                            # Note-on on the same tick but we already closed
                            # some previous notes -> it will continue, keep it.
                            last_note_on[key] = notes_to_keep
                        else:
                            # Remove the last note on for this instrument
                            del last_note_on[key]
                # Store pitch bends
                elif event.type == "pitchwheel":
                    # Create pitch bend class instance
                    bend = PitchBend(event.pitch, event.time)
                    # Get the program for the current inst
                    program = current_instrument[event.channel]
                    # Retrieve the Instrument instance for the current inst
                    # Don't create a new instrument if none exists
                    instrument = __get_instrument(
                        program, event.channel, track_idx, False
                    )
                    # Add the pitch bend event
                    instrument.pitch_bends.append(bend)
                # Store control changes
                elif event.type == "control_change":
                    control_change = ControlChange(
                        event.control, event.value, event.time
                    )
                    # Get the program for the current inst
                    program = current_instrument[event.channel]
                    # Retrieve the Instrument instance for the current inst
                    # Don't create a new instrument if none exists
                    instrument = __get_instrument(
                        program, event.channel, track_idx, False
                    )
                    # Add the control change event
                    instrument.control_changes.append(control_change)

                    # Process pedals
                    if (
                        ped_list and event.control == 64 and event.value == 0
                    ):  # pedal list not empty: already have 'on'
                        ped_list.append(event)  # Now have on and off
                        pedal = Pedal(ped_list[0].time, ped_list[1].time)
                        # Add the control change event
                        instrument.pedals.append(pedal)
                        ped_list = []
                    elif not ped_list and event.control == 64 and event.value == 127:
                        ped_list.append(event)  # Now only have on

        # Initialize list of instruments from instrument_map
        instruments = [i for i in instrument_map.values()]
        return instruments

    def get_tick_to_time_mapping(self) -> np.ndarray:
        return _get_tick_to_second_mapping(
            self.ticks_per_beat, self.max_tick, self.tempo_changes
        )

    @property
    def num_instruments(self) -> int:
        return len(self.instruments)

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        output_list = [
            f"ticks per beat: {self.ticks_per_beat}",
            f"max tick: {self.max_tick}",
            f"tempo changes: {len(self.tempo_changes)}",
            f"time sig: {len(self.time_signature_changes)}",
            f"key sig: {len(self.key_signature_changes)}",
            f"markers: {len(self.markers)}",
            f"lyrics: {bool(len(self.lyrics))}",
            f"instruments: {self.num_instruments}",
        ]
        output_str = "\n".join(output_list)
        return output_str

    def __eq__(self, other):
        # Similarly to `Instrument`, we check that the MIDIs attributes are respectively equal.
        if self.ticks_per_beat != other.ticks_per_beat:
            return False

        # Check list attributes.
        # These list should all contain objects that is either a dataclass or implements `__eq__`.
        lists_attr = [name for name, val in vars(self).items() if isinstance(val, list)]
        for list_attr in lists_attr:
            if len(getattr(self, list_attr)) != len(getattr(other, list_attr)):
                return False
            if any(
                a1 != a2
                for a1, a2 in zip(getattr(self, list_attr), getattr(other, list_attr))
            ):
                return False

        # All good, both MIDIs holds the exact same content
        return True

    def dump(
        self,
        filename: Optional[Union[str, Path]] = None,
        file=None,
        segment: Optional[Tuple[int, int]] = None,
        shift: bool = True,
        instrument_idx: Optional[int] = None,
        charset: str = "latin1",
    ):
        # comparison function
        def event_compare(event1, event2):
            if event1.time != event2.time:
                return event1.time - event2.time

            # If its two note_on (at the same tick), sort by expected note_off in a FIFO logic
            # This is required in case where the MIDI has notes starting at the same tick and one
            # with a higher duration is listed before one with a shorter one. In this case, the note
            # with the higher duration should come after, otherwise it will be ended first by the
            # following note_off event. Ultimately, as the notes have the same starting time and pitch,
            # the only thing that could be missed is their velocities. This check prevents this.
            if event1.type == event2.type == "note_on":
                return event1.end - event2.end

            secondary_sort = {
                "set_tempo": 1,
                "time_signature": 2,
                "key_signature": 3,
                "marker": 4,
                "lyrics": 5,
                "program_change": 6,
                "pitchwheel": 7,
                "control_change": 8,
                "note_off": 9,
                "note_on": 10,
                "end_of_track": 11,
            }

            if event1.type in secondary_sort and event2.type in secondary_sort:
                return secondary_sort[event1.type] - secondary_sort[event2.type]

            # Events have the same order / position, no change between position
            return 0

        if (filename is None) and (file is None):
            raise OSError("please specify the output.")

        if instrument_idx is None:
            pass
        elif isinstance(instrument_idx, int):
            instrument_idx = [instrument_idx]
        elif isinstance(instrument_idx, Sequence) and len(instrument_idx) == 0:
            pass
        else:
            raise ValueError("Invalid instrument index")

        # Create file
        midi_parsed = mido.MidiFile(ticks_per_beat=self.ticks_per_beat, charset=charset)

        # Create track 0 with timing information

        # 1. Time signature
        # add default
        add_ts = True
        ts_list = []
        if self.time_signature_changes:
            add_ts = min([ts.time for ts in self.time_signature_changes]) > 0
        if add_ts:
            ts_list.append(
                mido.MetaMessage("time_signature", time=0, numerator=4, denominator=4)
            )

        # add each
        for ts in self.time_signature_changes:
            ts_list.append(
                mido.MetaMessage(
                    "time_signature",
                    time=ts.time,
                    numerator=ts.numerator,
                    denominator=ts.denominator,
                )
            )

        # 2. Tempo
        # - add default
        add_t = True
        tempo_list = []
        if self.tempo_changes:
            add_t = min([t.time for t in self.tempo_changes]) > 0.0
        if add_t:
            tempo_list.append(
                mido.MetaMessage("set_tempo", time=0, tempo=mido.bpm2tempo(DEFAULT_BPM))
            )

        # - add each
        for t in self.tempo_changes:
            tempo_list.append(
                mido.MetaMessage(
                    "set_tempo", time=t.time, tempo=mido.bpm2tempo(t.tempo)
                )
            )

        # 3. Lyrics
        lyrics_list = []
        for lyr in self.lyrics:
            lyrics_list.append(mido.MetaMessage("lyrics", time=lyr.time, text=lyr.text))

        # 4. Markers
        markers_list = []
        for m in self.markers:
            markers_list.append(mido.MetaMessage("marker", time=m.time, text=m.text))

        # 5. Key
        key_list = []
        for ks in self.key_signature_changes:
            key_list.append(
                mido.MetaMessage("key_signature", time=ks.time, key=ks.key_name)
            )

        # crop segment
        start_tick, end_tick = 0, 0
        if segment:
            start_tick, end_tick = segment
            ts_list = _include_meta_events_within_tick_range(
                ts_list, start_tick, end_tick, shift=shift, front=True
            )
            tempo_list = _include_meta_events_within_tick_range(
                tempo_list, start_tick, end_tick, shift=shift, front=True
            )
            lyrics_list = _include_meta_events_within_tick_range(
                lyrics_list, start_tick, end_tick, shift=shift, front=False
            )
            markers_list = _include_meta_events_within_tick_range(
                markers_list, start_tick, end_tick, shift=shift, front=False
            )
            key_list = _include_meta_events_within_tick_range(
                key_list, start_tick, end_tick, shift=shift, front=True
            )
        meta_track = ts_list + tempo_list + lyrics_list + markers_list + key_list

        # sort
        meta_track.sort(key=functools.cmp_to_key(event_compare))

        # end of meta track
        meta_track.append(
            mido.MetaMessage("end_of_track", time=meta_track[-1].time + 1)
        )
        midi_parsed.tracks.append(meta_track)

        # -- instruments -- #
        channels = list(range(16))
        channels.remove(9)  # for durm
        for cur_idx, instrument in enumerate(self.instruments):
            if instrument_idx:
                if cur_idx not in instrument_idx:
                    continue

            track = mido.MidiTrack()
            # segment-free
            # track name
            if instrument.name:
                track.append(
                    mido.MetaMessage("track_name", time=0, name=instrument.name)
                )

            # If it's a drum event, we need to set channel to 9
            if instrument.is_drum:
                channel = 9

            # Otherwise, choose a channel from the possible channel list
            else:
                channel = channels[cur_idx % len(channels)]

            # Set the program number
            track.append(
                mido.Message(
                    "program_change",
                    time=0,
                    program=instrument.program,
                    channel=channel,
                )
            )

            # segment-related
            # Add all pitch bend events
            bend_list = []
            for bend in instrument.pitch_bends:
                bend_list.append(
                    mido.Message(
                        "pitchwheel", time=bend.time, channel=channel, pitch=bend.pitch
                    )
                )

            # Add all control change events
            cc_list = []
            if instrument.control_changes:
                for control_change in instrument.control_changes:
                    track.append(
                        mido.Message(
                            "control_change",
                            time=control_change.time,
                            channel=channel,
                            control=control_change.number,
                            value=control_change.value,
                        )
                    )
            else:
                for pedals in instrument.pedals:
                    # append for pedal-on (127)
                    cc_list.append(
                        mido.Message(
                            "control_change",
                            time=pedals.start,
                            channel=channel,
                            control=64,
                            value=127,
                        )
                    )
                    # append for pedal-off (0)
                    cc_list.append(
                        mido.Message(
                            "control_change",
                            time=pedals.end,
                            channel=channel,
                            control=64,
                            value=0,
                        )
                    )

            if segment:
                cc_list = _include_meta_events_within_tick_range(
                    cc_list, start_tick, end_tick, shift=shift, front=False
                )
                bend_list = _include_meta_events_within_tick_range(
                    bend_list, start_tick, end_tick, shift=shift, front=True
                )
            track += bend_list + cc_list

            # Add all note events
            for note in instrument.notes:
                if segment and not _is_note_within_tick_range(
                    note, start_tick, end_tick, shift, True
                ):
                    continue
                track.append(
                    mido.Message(
                        "note_on",
                        time=note.start,
                        channel=channel,
                        note=note.pitch,
                        velocity=note.velocity,
                        end=note.end,
                    )
                )
                # Also need a note-off event
                track.append(
                    mido.Message(
                        "note_off",
                        time=note.end,
                        channel=channel,
                        note=note.pitch,
                        velocity=note.velocity,
                    )
                )
            track = sorted(track, key=functools.cmp_to_key(event_compare))

            # Finally, add in an end of track event
            track.append(mido.MetaMessage("end_of_track", time=track[-1].time + 1))
            # Add to the list of output tracks
            midi_parsed.tracks.append(track)

        # Cumulative timing to delta
        for track in midi_parsed.tracks:
            tick = 0
            for event in track:
                event.time -= tick
                tick += event.time

        # Write it out
        if filename:
            midi_parsed.save(filename=filename)
        else:
            midi_parsed.save(file=file)


def _is_note_within_tick_range(
    note: Note,
    start_tick: int,
    end_tick: int,
    shift: bool = False,
    adapt_note_times: bool = False,
) -> bool:
    r"""

    Args:
        note: note to check.
        start_tick: starting tick.
        end_tick: ending tick.
        shift: if True, will shift the note's start and end times by `start_tick`.
        adapt_note_times: if True, will cut the start and end note times to fit within the range.

    Returns: whether the note is within the time range.

    """
    #             |              |
    #    ****     |  ***       **|*     *****
    tmp_st = max(start_tick, note.start)
    tmp_ed = max(start_tick, min(note.end, end_tick))
    if (tmp_ed - tmp_st) <= 0:
        return False

    if shift:
        tmp_st -= start_tick
        tmp_ed -= start_tick
    if adapt_note_times:
        note.start = tmp_st
        note.end = tmp_ed
    return True


def _include_meta_events_within_tick_range(
    events: Sequence[Union[mido.MetaMessage, mido.Message]],
    start_tick: int,
    end_tick: int,
    shift: bool = False,
    front: bool = True,
) -> Sequence[mido.MetaMessage]:
    r"""

    Args:
        events: meta messages to check.
        start_tick: starting tick.
        end_tick: ending tick.
        shift: if True, will shift the note's start and end times by `start_tick`.
        front: will make sure the message coming last before the `start_tick` is kept and its time set at `start_tick`.

    Returns: list of meta messages within the given tick range

    """
    proc_events = []
    num = len(events)
    if not events:
        return events

    # include events from back
    i = num - 1
    while i >= 0:
        event = events[i]
        if event.time < start_tick:
            break
        if event.time < end_tick:
            proc_events.append(event)
        i -= 1

    # if the first tick has no event, add the previous one
    if front and (i >= 0):
        if not proc_events:
            proc_events = [events[i]]
        elif proc_events[-1].time != start_tick:
            proc_events.append(events[i])
        proc_events[-1].time = start_tick

    # reverse
    proc_events = proc_events[::-1]

    # shift
    if shift:
        for event in proc_events:
            event.time -= start_tick
            event.time = int(max(event.time, 0))

    return proc_events


def _get_tick_eq_of_second(sec: Union[float, int], tick_to_time: np.ndarray) -> int:
    return int((np.abs(tick_to_time - sec)).argmin())


def _get_tick_to_second_mapping(
    ticks_per_beat: int, max_tick: int, tempo_changes: Sequence[TempoChange]
) -> np.ndarray:
    tick_to_time = np.zeros(max_tick + 1)
    num_tempi = len(tempo_changes)
    acc_time = 0

    for idx in range(num_tempi):
        start_tick = tempo_changes[idx].time
        cur_tempo = tempo_changes[idx].tempo

        # compute tick scale
        seconds_per_beat = 60 / cur_tempo
        seconds_per_tick = seconds_per_beat / float(ticks_per_beat)

        # set end tick of interval
        end_tick = tempo_changes[idx + 1].time if (idx + 1) < num_tempi else max_tick

        # write interval
        ticks = np.arange(end_tick - start_tick + 1)
        tick_to_time[start_tick : end_tick + 1] = acc_time + seconds_per_tick * ticks
        acc_time = tick_to_time[end_tick]
    return tick_to_time
