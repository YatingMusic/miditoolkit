import re
import mido
import warnings
import functools
import collections
import numpy as np
from copy import deepcopy
from .containers import KeySignature, TimeSignature, Lyric, Note, PitchBend, ControlChange, Instrument, TempoChange, Marker, Pedal


DEFAULT_BPM = int(120)


class MidiFile(object):
    def __init__(self, filename=None, file=None, ticks_per_beat=480, clip=False, charset ='latin1'):
        # create empty file
        if (filename is None and file is None):
            self.ticks_per_beat = ticks_per_beat 
            self.max_tick = 0
            self.tempo_changes = []
            self.time_signature_changes = []
            self.key_signature_changes = []
            self.lyrics = []
            self.markers = []
            self.instruments = []
        
        # load
        else:
            if filename:
                # filename
                mido_obj = mido.MidiFile(filename=filename, clip=clip, charset=charset)
            else:
                mido_obj = mido.MidiFile(file=file, clip=clip, charset=charset)
            

            # ticks_per_beat
            self.ticks_per_beat = mido_obj.ticks_per_beat

            # convert delta time to cumulative time
            mido_obj = self._convert_delta_to_cumulative(mido_obj)

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
        

    def _convert_delta_to_cumulative(self, mido_obj):
        for track in mido_obj.tracks:
            tick = int(0)
            for event in track:
                event.time += tick
                tick = event.time
        return mido_obj

    def _load_tempo_changes(self, mido_obj):
        # default bpm
        tempo_changes = [TempoChange(DEFAULT_BPM, 0)]

        # traversing
        for track in mido_obj.tracks:
            for event in track:
                if event.type == 'set_tempo':
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

    def _load_time_signatures(self, mido_obj):
        # no default
        time_signature_changes = []

        # traversing
        for track in mido_obj.tracks:
            for event in track:
                if event.type == 'time_signature':
                    ts_obj = TimeSignature(
                        event.numerator,
                        event.denominator,
                        event.time)
                    time_signature_changes.append(ts_obj)
        return time_signature_changes

    def _load_key_signatures(self, mido_obj):
        # no default
        key_signature_changes = []

        # traversing
        for track in mido_obj.tracks:
            for event in track:
                if event.type == 'key_signature':
                    key_obj = KeySignature(
                        event.key, 
                        event.time)
                    key_signature_changes.append(key_obj)
        return key_signature_changes

    def _load_markers(self, mido_obj):
        # no default
        markers = []

        # traversing
        for track in mido_obj.tracks:
            for event in track:
                if event.type == 'marker':
                    markers.append(Marker(event.text, event.time))
        return markers

    def _load_lyrics(self, mido_obj):
        # no default
        lyrics = []
        
        # traversing
        for track in mido_obj.tracks:
            for event in track:
                if event.type == 'lyrics':
                    lyrics.append(Lyric(event.text, event.time))
        return lyrics

    def _load_instruments(self, midi_data):
        instrument_map = collections.OrderedDict()
        # Store a similar mapping to instruments storing "straggler events",
        # e.g. events which appear before we want to initialize an Instrument
        stragglers = {}
        # This dict will map track indices to any track names encountered
        track_name_map = collections.defaultdict(str)

        def __get_instrument(program, channel, track, create_new):
            """Gets the Instrument corresponding to the given program number,
            drum/non-drum type, channel, and track index.  If no such
            instrument exists, one is created.

            """
            # If we have already created an instrument for this program
            # number/track/channel, return it
            if (program, channel, track) in instrument_map:
                return instrument_map[(program, channel, track)]
            # If there's a straggler instrument for this instrument and we
            # aren't being requested to create a new instrument
            if not create_new and (channel, track) in stragglers:
                return stragglers[(channel, track)]
            # If we are told to, create a new instrument and store it
            if create_new:
                is_drum = (channel == 9)
                instrument = Instrument(
                    program, is_drum, track_name_map[track_idx])
                # If any events appeared for this instrument before now,
                # include them in the new instrument
                if (channel, track) in stragglers:
                    straggler = stragglers[(channel, track)]
                    instrument.control_changes = straggler.control_changes
                    instrument.pitch_bends = straggler.pitch_bends
                    instrument.pedals = straggler.pedals
                # Add the instrument to the instrument map
                instrument_map[(program, channel, track)] = instrument
            # Otherwise, create a "straggler" instrument which holds events
            # which appear before we actually want to create a proper new
            # instrument
            else:
                # Create a "straggler" instrument
                instrument = Instrument(program, track_name_map[track_idx])
                # Note that stragglers ignores program number, because we want
                # to store all events on a track which appear before the first
                # note-on, regardless of program
                stragglers[(channel, track)] = instrument
            return instrument

            
        for track_idx, track in enumerate(midi_data.tracks):
            # Keep track of last note on location:
            # key = (instrument, note),
            # value = (note-on tick, velocity)
            last_note_on = collections.defaultdict(list)
            # Keep track of which instrument is playing in each channel
            # initialize to program 0 for all channels
            current_instrument = np.zeros(16, dtype=np.int)
            ped_list = []
            for event in track:
                # Look for track name events
                if event.type == 'track_name':
                    # Set the track name for the current track
                    track_name_map[track_idx] = event.name
                # Look for program change events
                if event.type == 'program_change':
                    # Update the instrument for this channel
                    current_instrument[event.channel] = event.program
                # Note ons are note on events with velocity > 0
                elif event.type == 'note_on' and event.velocity > 0:
                    # Store this as the last note-on location
                    note_on_index = (event.channel, event.note)
                    last_note_on[note_on_index].append((
                        event.time, event.velocity))
                # Note offs can also be note on events with 0 velocity
                elif event.type == 'note_off' or (event.type == 'note_on' and
                                                  event.velocity == 0):
                    # Check that a note-on exists (ignore spurious note-offs)
                    key = (event.channel, event.note)
                    if key in last_note_on:
                        # Get the start/stop times and velocity of every note
                        # which was turned on with this instrument/drum/pitch.
                        # One note-off may close multiple note-on events from
                        # previous ticks. In case there's a note-off and then
                        # note-on at the same tick we keep the open note from
                        # this tick.
                        end_tick = event.time
                        open_notes = last_note_on[key]

                        notes_to_close = [
                            (start_tick, velocity)
                            for start_tick, velocity in open_notes
                            if start_tick != end_tick]
                        notes_to_keep = [
                            (start_tick, velocity)
                            for start_tick, velocity in open_notes
                            if start_tick == end_tick]

                        for start_tick, velocity in notes_to_close:
                            start_time = start_tick
                            end_time = end_tick
                            # Create the note event
                            note = Note(velocity, event.note, start_time,
                                        end_time)
                            # Get the program and drum type for the current
                            # instrument
                            program = current_instrument[event.channel]
                            # Retrieve the Instrument instance for the current
                            # instrument
                            # Create a new instrument if none exists
                            instrument = __get_instrument(
                                program, event.channel, track_idx, 1)
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
                elif event.type == 'pitchwheel':
                    # Create pitch bend class instance
                    bend = PitchBend(event.pitch, event.time)
                    # Get the program for the current inst
                    program = current_instrument[event.channel]
                    # Retrieve the Instrument instance for the current inst
                    # Don't create a new instrument if none exists
                    instrument = __get_instrument(
                        program, event.channel, track_idx, 0)
                    # Add the pitch bend event
                    instrument.pitch_bends.append(bend)
                # Store control changes
                elif event.type == 'control_change':
                    control_change = ControlChange(
                        event.control, event.value, event.time)
                    # Get the program for the current inst
                    program = current_instrument[event.channel]
                    # Retrieve the Instrument instance for the current inst
                    # Don't create a new instrument if none exists
                    instrument = __get_instrument(
                        program, event.channel, track_idx, 0)
                    # Add the control change event
                    instrument.control_changes.append(control_change)

                    # Process pedals
                    if ped_list and event.control == 64 and event.value == 0:  # pedal list not empty: already have 'on'
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
    
    
    
    def get_tick_to_time_mapping(self):
        return _get_tick_to_time_mapping(
            self.ticks_per_beat, 
            self.max_tick, 
            self.tempo_changes)

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        output_list = [
            "ticks per beat: {}".format(self.ticks_per_beat),
            "max tick: {}".format(self.max_tick),
            "tempo changes: {}".format(len(self.tempo_changes)),
            "time sig: {}".format(len(self.time_signature_changes)),
            "key sig: {}".format(len(self.key_signature_changes)),
            'markers: {}'.format(len(self.markers)),
            "lyrics: {}".format(bool(len(self.lyrics))),
            "instruments: {}".format(len(self.instruments))
        ] 
        output_str = "\n".join(output_list)
        return output_str

    def dump(self, 
             filename=None, 
             file=None, 
             segment=None, 
             shift=True, 
             instrument_idx=None,
             charset ='latin1'):

        # comparison function
        def event_compare(event1, event2):
            secondary_sort = {
                'set_tempo': lambda e: (1 * 256 * 256),
                'time_signature': lambda e: (2 * 256 * 256),
                'key_signature': lambda e: (3 * 256 * 256),
                'marker': lambda e: (4 * 256 * 256),
                'lyrics': lambda e: (5 * 256 * 256),
                'program_change': lambda e: (6 * 256 * 256),
                'pitchwheel': lambda e: ((7 * 256 * 256) + e.pitch),
                'control_change': lambda e: (
                    (8 * 256 * 256) + (e.control * 256) + e.value),
                'note_off': lambda e: ((9 * 256 * 256) + (e.note * 256)),
                'note_on': lambda e: (
                    (10 * 256 * 256) + (e.note * 256) + e.velocity),
                'end_of_track': lambda e: (11 * 256 * 256)
            }
            if (event1.time == event2.time and
                    event1.type in secondary_sort and
                    event2.type in secondary_sort):
                return (secondary_sort[event1.type](event1) -
                        secondary_sort[event2.type](event2))

            return event1.time - event2.time

        if (filename is None) and (file is None):
            raise IOError('please specify the output.')

        if instrument_idx is None:
            pass
        elif len(instrument_idx)==0:
            return
        elif isinstance(instrument_idx, int):
            instrument_idx = [instrument_idx]
        elif isinstance(instrument_idx, list):
            pass
        else:
            raise ValueError('Invalid instrument index')

        # crop segment
        if segment is not None:
            if not isinstance(segment, list) and not isinstance(segment, tuple):
                raise ValueError('Invalid segment format')
            start_tick = segment[0]
            end_tick= segment[1]

        # Create file
        midi_parsed = mido.MidiFile(ticks_per_beat=self.ticks_per_beat, charset=charset)

        # Create track 0 with timing information
        meta_track = mido.MidiTrack()

        # -- meta track -- #
        # 1. Time signature
        # add default
        add_ts = True
        ts_list = []
        if self.time_signature_changes:
            add_ts = min([ts.time for ts in self.time_signature_changes]) > 0.0
        if add_ts:
            ts_list.append(
                mido.MetaMessage(
                    'time_signature', 
                    time=0, 
                    numerator=4, 
                    denominator=4))

        # add each
        for ts in self.time_signature_changes:
            ts_list.append(
                mido.MetaMessage(
                    'time_signature', 
                    time=ts.time,
                    numerator=ts.numerator, 
                    denominator=ts.denominator))
        
        # 2. Tempo
        # - add default
        add_t = True
        tempo_list = [] 
        if self.tempo_changes:
            add_t = min([t.time for t in self.tempo_changes]) > 0.0
        if add_t:
            tempo_list.append(
                mido.MetaMessage(
                    'set_tempo', 
                    time=0, 
                    tempo=mido.bpm2tempo(DEFAULT_BPM)))

        # - add each
        for t in self.tempo_changes:
            tempo_list.append(
                mido.MetaMessage(
                    'set_tempo',
                    time=t.time,
                    tempo=mido.bpm2tempo(t.tempo)))
        
        # 3. Lyrics
        lyrics_list = []
        for l in self.lyrics:
            lyrics_list.append(
                mido.MetaMessage(
                    'lyrics', 
                    time=l.time, 
                    text=l.text))   

        # 4. Markers
        markers_list = []
        for m in self.markers:
            markers_list.append(
                mido.MetaMessage(
                    'marker', 
                    time=m.time, 
                    text=m.text))   

        # 5. Key
        key_number_to_mido_key_name = [
            'C', 'Db', 'D', 'Eb', 'E', 'F', 'F#', 'G', 'Ab', 'A', 'Bb', 'B',
            'Cm', 'C#m', 'Dm', 'D#m', 'Em', 'Fm', 'F#m', 'Gm', 'G#m', 'Am',
            'Bbm', 'Bm']
        key_list = []
        for ks in self.key_signature_changes:
            key_list.append(mido.MetaMessage(
                'key_signature', time=ks.time,
                key=key_number_to_mido_key_name[ks.key_number]))

        if segment:
            ts_list = _include_meta_events_within_range(ts_list, start_tick, end_tick, shift=shift, front=True)
            tempo_list = _include_meta_events_within_range(tempo_list, start_tick, end_tick, shift=shift, front=True)
            lyrics_list = _include_meta_events_within_range(lyrics_list, start_tick, end_tick, shift=shift, front=False)
            markers_list = _include_meta_events_within_range(markers_list, start_tick, end_tick, shift=shift, front=False)
            key_list = _include_meta_events_within_range(key_list, start_tick, end_tick, shift=shift, front=True)
        meta_track = ts_list + tempo_list + lyrics_list+ markers_list + key_list 

        # sort
        meta_track.sort(key=functools.cmp_to_key(event_compare))

        # end of meta track
        meta_track.append(mido.MetaMessage(
            'end_of_track', time=meta_track[-1].time + 1))
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
                track.append(mido.MetaMessage(
                    'track_name', time=0, name=instrument.name))

            # If it's a drum event, we need to set channel to 9
            if instrument.is_drum:
                channel = 9

            # Otherwise, choose a channel from the possible channel list
            else:
                channel = channels[cur_idx % len(channels)]

            # Set the program number
            track.append(mido.Message(
                'program_change', time=0, program=instrument.program,
                channel=channel))
            
            # segment-related
            # Add all pitch bend events
            bend_list = []
            for bend in instrument.pitch_bends:
                bend_list.append(mido.Message(
                    'pitchwheel', time=bend.time,
                    channel=channel, pitch=bend.pitch))
           
            # Add all control change events
            cc_list = []
            if instrument.control_changes:
                for control_change in instrument.control_changes:
                    track.append(mido.Message(
                        'control_change',
                        time=control_change.time,
                        channel=channel, control=control_change.number,
                        value=control_change.value))
            else:
                for pedals in instrument.pedals:
                    # append for pedal-on (127)
                    cc_list.append(mido.Message(
                        'control_change',
                        time=pedals.start,
                        channel=channel, control=64,
                        value=127))
                    
                    # append for pedal-off (0)
                    cc_list.append(mido.Message(
                        'control_change',
                        time=pedals.end,
                        channel=channel, control=64,
                        value=0))
                    #print(cc_list[-2:])


            if segment:
                bend_list = _include_meta_events_within_range(bend_list, start_tick, end_tick, shift=shift, front=True)
            track += (bend_list + cc_list)  # 

            # Add all note events
            for note in instrument.notes:
                if segment:
                    note = _check_note_within_range(note, start_tick, end_tick, shift=True)
                if note:
                    track.append(mido.Message(
                        'note_on', time=note.start,
                        channel=channel, note=note.pitch, velocity=note.velocity))
                    # Also need a note-off event (note on with velocity 0)
                    track.append(mido.Message(
                        'note_on', time=note.end,
                        channel=channel, note=note.pitch, velocity=0))
            track = sorted(track, key=functools.cmp_to_key(event_compare))
            
            memo = 0
            i = 0
            while i < len(track):
                #print(i)
                #print(len(track))
                if track[i].type == 'control_change':
                    tmp = track[i].value
                    if tmp == memo:
                        track.pop(i)
                    else:
                        memo = track[i].value
                        i += 1
                else:
                    i += 1
                
            
            #i = 0
            #while i <= len(cc_list)-1:
            #    assert cc_list[i].value == 127
            #    if cc_list[i].time < track[0].time:
            #        track.insert(0, cc_list[i])
            #        track.insert(0, cc_list[i+1])
            #        i = i+2
            #    else:
            #        for j in range(len(track)-1):
            #            if track[j].time <= cc_list[i].time < track[j+1].time:
            #                track.insert(j+1, cc_list[i])
            #                track.insert(j+2, cc_list[i+1])
            #                i = i+2
            #                break
                    
            # If there's a note off event and a note on event with the same
            # tick and pitch, put the note off event first
            for n, (event1, event2) in enumerate(zip(track[:-1], track[1:])):
                if (event1.time == event2.time and
                        event1.type == 'note_on' and
                        event2.type == 'note_on' and
                        event1.note == event2.note and
                        event1.velocity != 0 and
                        event2.velocity == 0):
                    track[n] = event2
                    track[n + 1] = event1

            # Finally, add in an end of track event
            track.append(mido.MetaMessage(
                'end_of_track', time=track[-1].time + 1))
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


def _check_note_within_range(note, st, ed, shift=True):
    tmp_st = max(st, note.start)
    tmp_ed = max(st, min(note.end, ed))

    if (tmp_ed - tmp_st) <= 0:
        return None
    if shift:
        tmp_st -= st
        tmp_ed -= st
    note.start = int(tmp_st)
    note.end = int(tmp_ed)
    return note


def _include_meta_events_within_range(events, st, ed, shift=True, front=True):
    '''
    For time, key signatutr
    '''
    proc_events = []
    num = len(events)
    if not events:
        return events
        
    # include events from back
    i = num - 1
    while i >= 0:
        event = events[i]
        if event.time < st:
            break
        if event.time < ed:
            proc_events.append(event)
        i -= 1

    # if the first tick has no event, add the previous one
    if front and (i >= 0):
        if not proc_events:
            proc_events = [events[i]]
        elif proc_events[-1].time != st:
            proc_events.append(events[i])
        else:
            pass

    # reverse
    proc_events = proc_events[::-1]

    # shift
    result = []
    shift = st if shift else 0
    for event in proc_events:
        event.time -= st
        event.time = int(max(event.time, 0))
        result.append(event)
    return proc_events
        

def _find_nearest_np(array, value):
    return (np.abs(array - value)).argmin()


def _get_tick_index_by_seconds(sec, tick_to_time):
    if not isinstance(sec, float):
        raise ValueError('Seconds should be float')

    if isinstance(sec, list) or isinstance(sec, tuple):
        return [_find_nearest_np(tick_to_time, s) for s in sec]
    else:
        return _find_nearest_np(tick_to_time, sec)


def _get_tick_to_time_mapping(ticks_per_beat, max_tick, tempo_changes):
    tick_to_time = np.zeros(max_tick + 1)
    num_tempi = len(tempo_changes)

    fianl_tick = max_tick
    acc_time = 0

    for idx in range(num_tempi):
        start_tick = tempo_changes[idx].time
        cur_tempo = tempo_changes[idx].tempo

        # compute tick scale
        seconds_per_beat = 60 / cur_tempo
        seconds_per_tick = seconds_per_beat / float(ticks_per_beat)

        # set end tick of interval
        end_tick = tempo_changes[idx + 1].time if (idx + 1) < num_tempi else fianl_tick

        # wrtie interval
        ticks = np.arange(end_tick - start_tick + 1)
        tick_to_time[start_tick:end_tick + 1] = (acc_time + seconds_per_tick *ticks)
        acc_time = tick_to_time[end_tick]
    return tick_to_time
