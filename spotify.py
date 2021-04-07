import spotipy
import spotipy.util as util
from spotipy.oauth2 import SpotifyClientCredentials
import os
import pandas as pd
from config import SPOTIFY_CLIENT_ID, SPOTIFY_CLIENT_SECRET


spotify = spotipy.Spotify(client_credentials_manager=SpotifyClientCredentials(client_id=SPOTIFY_CLIENT_ID, client_secret=SPOTIFY_CLIENT_SECRET))

def get_song_id(artist, song):
    # assume that the first result is the correct song
    # if song title has parentheticals, remove them
    while '(' in song:
        i1 = song.find('(')
        i2 = song.find(')')
        song = song[:i1] + song[i2+1:]
    results = spotify.search(q=f'{artist} {song}', limit=1, type="track")
    if len(results['tracks']['items']) == 0:
        return ""
    item = results['tracks']['items'][0]
    song_uri = item['uri'][14:]
    return song_uri


def get_song_info(artist, song):
    # assume that the first result is the correct song
    results = spotify.search(q=f'{artist} {song}', limit=1, type="track")
    item = results['tracks']['items'][0]
    artist_uri = item['artists'][0]['uri'] # just go with the first artist if there are multiple
    song_uri = item['uri']
    duration_ms = item['duration_ms']
    explicit = item['explicit']
    album = item['album']['name']
    popularity = item['popularity']
    return artist, artist_uri, song, song_uri, duration_ms, explicit, album, popularity

def add_features(users_songs):
    user_dfs = []
    for user_songs in users_songs:
        user1_list = []
        for song in user_songs['song_uri']:
            row = spotify.audio_features(tracks=[song])
            row = pd.DataFrame(row)
            user1_list.append(row)
        user1_df = pd.concat(user1_list)
        user1_df['weight'] = user_songs['weight']
        user_dfs.append(user1_df)

    dfs = pd.concat(user_dfs)
    # drop unnecessary features
    dfs.drop(['type','track_href','analysis_url','time_signature','duration_ms','uri','instrumentalness','liveness','loudness','key','mode'],1,inplace=True)
    dfs.set_index('id',inplace=True)
    return dfs

def get_recs(recs, N=30):
    result = []
    total_weight = sum([w * len(r) for r, w in recs])
    total_recs = 0
    for rec, weight in recs:
        num_recs = int(round(N * weight * len(rec) / total_weight))
        if num_recs <= 0:
            continue
        result.append(spotify.recommendations(seed_tracks=rec,limit=num_recs))
        total_recs += num_recs
    return result, total_recs

def info_from_id(song_id):
    track = spotify.track(song_id)
    return track