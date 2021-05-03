from flask import Flask, request
from flask_cors import CORS, cross_origin
import spotipy
import sys
from spotipy.oauth2 import SpotifyOAuth, SpotifyClientCredentials
import spotipy
import spotipy.util as util
import requests
import librosa
from flask import jsonify
from pydub import AudioSegment
import audio
import storage

app = Flask(__name__)

cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'


def get_other_options(sp: spotipy.Spotify, artist_ids):
    names = []
    for artist_id in artist_ids:
        related_artists = sp.artist_related_artists(artist_id)
        related_artists_names = [artist for artist in related_artists['artists'] if artist]
        names.extend(related_artists_names)

    return names



@app.route("/", methods=['POST'])
@cross_origin()
def index():
    content = request.json
    code = content['code']
    sp = spotipy.Spotify(auth=code)

    user_tracks = sp.current_user_saved_tracks()['items']
    results = []
    for item in user_tracks[:5]:
        track = item['track']
        preview_url = track["preview_url"]

        if preview_url != None:
            related_artists = get_other_options(sp, [artist['id'] for artist in track['artists']])
            url = audio.process_audio_and_upload(preview_url)

            results.append({
                'url': url,
                'options': related_artists
            })

    return jsonify(results)


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
