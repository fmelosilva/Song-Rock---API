import random
import sys
import time

import librosa
import requests
import spotipy
import spotipy.util as util
from flask import Flask, jsonify, request
from flask_cors import CORS, cross_origin
from spotipy.oauth2 import SpotifyClientCredentials, SpotifyOAuth

import audio
import storage

app = Flask(__name__)

cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'


def get_other_options(sp: spotipy.Spotify, artist_ids):
    options = []
    for artist_id in artist_ids:
        related_artists = sp.artist_related_artists(artist_id)
        filtered_artists = [{'artist': artist['name'], 'rightOption': False}
                            for artist in related_artists['artists']
                            if artist['id'] not in artist_ids]
        options.extend(filtered_artists)

    return random.sample(options, 3)


@app.route("/", methods=['POST'])
@cross_origin()
def index():
    content = request.json
    code = content['code']
    songs = 5 if 'songs' not in content else content['songs']
    sp = spotipy.Spotify(auth=code)

    user_tracks = sp.current_user_saved_tracks()['items']
    results = []
    tracks_with_preview = list(
        filter(lambda track: 'preview_url' in track['track'], user_tracks))

    if len(tracks_with_preview) < songs:
        return jsonify({
            'error': 'user does not have enough songs'
        })
    for item in random.sample(tracks_with_preview, songs):
        track = item['track']
        preview_url = track["preview_url"]
        artists = track['artists']
        options = [{
            'artist': artists[0]['name'],
            'rightOption': True
        }]

        options.extend(get_other_options(
            sp, [artist['id'] for artist in artists]))
        url = audio.process_audio_and_upload(preview_url)
        results.append({
            'url': url,
            'options': options
        })

    return jsonify(results)


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
