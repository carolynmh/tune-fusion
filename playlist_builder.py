# Libraries
from spotipy.client import Spotify
import sys
import pandas as pd
import os
import spotipy
import spotipy.util as util
from spotipy.oauth2 import SpotifyClientCredentials
import script
from config import SPOTIFY_CLIENT_ID, SPOTIFY_CLIENT_SECRET

redirect_uri = 'http://localhost:8000'
scope = "playlist-modify-private"

def default_playlist_name(names):
    if len(names) == 2:
        return f"{names[0]} and {names[1]}'s joint playlist"
    s = ""
    for i in range(len(names) - 1):
        s += f"{names[i]}, "
    s += f"and {names[i]}'s fused playlist"
    return s

# Builds playlist and returns new Playlist object
def new_playlist(sp, username, playlist_name, playlist_description):
    playlist = sp.user_playlist_create(username, playlist_name, public = False, description = playlist_description)
    return playlist

# this is the magical function right here
def create_joint_playlist(usernames, input_playlist_name):
    input_playlist_name = input_playlist_name.strip()
    if input_playlist_name == "":
        input_playlist_name = default_playlist_name(usernames)

    # use last.fm data and spotify features to gather a list of song ids
    fused_list, err = script.get_shared_playlist(usernames)
    return (fused_list, input_playlist_name), err
    

def make_spotify_playlist(fused_list, username, playlist_name):
    # Authorize
    token = util.prompt_for_user_token(username, scope, SPOTIFY_CLIENT_ID, SPOTIFY_CLIENT_SECRET, redirect_uri)
    if token:
        sp = spotipy.Spotify(auth=token)
    else:
        return f"Can't get token for {username}", True
    
    # Create the new playlist and get the playlist id
    pl = new_playlist(sp, username, playlist_name, 'Made with tune-fusion: https://uncommon.carolynmh.repl.co/testpage')
    new_id = pl['id']

    # Add Tracks
    song_ids = [track[-1] for track in fused_list]
    sp.user_playlist_add_tracks(username, new_id, tracks=song_ids, position=None)
    return "Success!", False

# for testing purposes
if __name__ == "__main__":
    # name1 = input("Your last.fm username: ")
    # name2 = input("Your friend's last.fm username: ")
    # playlist_name = input("Playlist name: ")
    msg, err = create_joint_playlist(['hamrobe', 'didntask', 'lynmarie44'], "")
    if err:
        print(msg)
    else:
        make_spotify_playlist(msg[0], 'hamrobe', msg[1])
