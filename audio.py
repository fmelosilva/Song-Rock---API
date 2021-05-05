import tempfile
from enum import Enum

import auditok
import librosa
import numpy as np
import requests
import soundfile as sf
from spleeter.separator import Codec, Separator

import storage

separator = Separator('spleeter:5stems')


class SpleeterTrack(Enum):
    DRUMS_TRACK = 'drums'
    VOCALS_TRACK = 'vocals'
    OTHER_TRACK = 'other'
    PIANO_TRACK = 'piano'
    BASS_TRACK = 'bass'


def resolve_spleeter_track_path(directory, track: SpleeterTrack):
    return f'{directory}/{track.value}.wav'


def resolve_all_spleeter_tracks_path(directory):
    return [resolve_spleeter_track_path(directory, track) for track in SpleeterTrack]


def download_from_url(url: str, filename: str):
    results = requests.get(url)
    with open(filename, 'wb') as f:
        f.write(results.content)


def overlay_all(audio_names, output_filename):
    audios = []
    for audio in audio_names:
        y, sr = librosa.load(audio)
        audios.append(y)

    result = sum(audios) / len(audios)
    sf.write(output_filename, result, sr, 'PCM_24')


def apply_pitch_shift(filename: str):
    y, sr = librosa.load(filename)
    y = librosa.effects.pitch_shift(y, sr, n_steps=-12)

    sf.write(filename, y, sr, 'PCM_24')


def get_noise_duration(filename: str):
    audio_regions = auditok.split(
        filename,
        min_dur=0.2,     # minimum duration of a valid audio event in seconds
        max_dur=4,       # maximum duration of an event
        max_silence=0.3,  # maximum duration of tolerated continuous silence within an event
        energy_threshold=55  # threshold of detection
    )

    noise_duration = 0.0

    for i, r in enumerate(audio_regions):
        noise_duration += (r.meta.end - r.meta.start)

    return noise_duration


def get_duration(filename: str):
    y, sr = librosa.load(filename)

    return librosa.get_duration(y, sr)


def modify_audio(filename: str, output_filename: str):
    with tempfile.TemporaryDirectory() as tmpdirname:
        separator.separate_to_file(
            filename, tmpdirname, codec=Codec.WAV, filename_format='{instrument}.wav')
        vocals_path = resolve_spleeter_track_path(
            tmpdirname, SpleeterTrack.VOCALS_TRACK)
        apply_pitch_shift(vocals_path)
        tracks = resolve_all_spleeter_tracks_path(tmpdirname)
        overlay_all(tracks, output_filename)


def process_audio_and_upload(url: str):
    with tempfile.NamedTemporaryFile(suffix='.mp3') as source_file, tempfile.NamedTemporaryFile(suffix='.wav') as output_file:
        download_from_url(url, source_file.name)
        modify_audio(source_file.name, output_file.name)
        
        return storage.upload(output_file.name)
