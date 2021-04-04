import numpy as np
from spotipy.client import Spotify
import lastfm
import pylast
import pandas as pd
import spotify
from sklearn.cluster import KMeans
from sklearn.preprocessing import MinMaxScaler, StandardScaler
from sklearn.decomposition import PCA 
import random

# number of tracks from each user
NUM_SONGS_FROM_USERS = 50
NUM_CLUSTERS = 20
    
def get_df(tracks):
    weights = []
    artists = []
    songs = []
    artist_uris = []
    song_uris = []
    durations = []
    explicits = []
    albums = []
    popularities = []
    for track in tracks:
        item = track.item
        weight = track.weight
        weights.append(weight)
        artist = item.artist.name
        artists.append(item.artist.name)
        song = item.title
        songs.append(item.title)
        # lastfm's "similar" only works on some
        # similar = item.get_similar(limit=2)
        # print(item.title, similar)
        _, artist_uri, _, song_uri, duration_ms, explicit, album, popularity = spotify.get_song_info(artist=artist, song=song)
        artist_uris.append(artist_uri)
        song_uris.append(song_uri)
        durations.append(duration_ms)
        explicits.append(explicit)
        albums.append(album)
        popularities.append(popularity)

    df = pd.DataFrame(
        {'artist': artists,
        'artist_uri': artist_uris,
        'song': songs,
        'song_uri': song_uris,
        'duration_ms': durations,
        'explicit': explicits,
        'album': albums,
        'popularity': popularities,
        'weight': weights
    })
    return df

# Create list of lists of song ids to put into recommendation function
# this is the "main algorithm" where all the data science happens
def get_list_of_recs(dfs, all_songs):
    columns = ['danceability','energy','speechiness','acousticness','valence','tempo']
    scaler = MinMaxScaler()
    scaler.fit(dfs[columns])
    dfs[columns] = scaler.transform(dfs[columns])
    scaler = StandardScaler()
    scaler.fit(dfs[['weight']])
    dfs[['weight']] = scaler.transform(dfs[['weight']])
    dfs[['weight']] -= np.min(dfs[['weight']]) - 0.4

    kmeans = KMeans(n_clusters=NUM_CLUSTERS)
    kmeans.fit(dfs)
    # scaler = MinMaxScaler()
    # scaled = scaler.fit_transform(dfs)
    y_kmeans = kmeans.fit_predict(dfs)
    dfs['cluster'] = y_kmeans
    dfs['artist'] = all_songs.artist.tolist()
    dfs['title'] = all_songs.song.tolist()
    
    # remove clusters with only one song in them
    delete_clusters = []
    cluster = 0
    while cluster < (len(dfs.cluster.unique())-1):
        if dfs.groupby('cluster').count().loc[cluster].danceability <= 1:
            delete_clusters.append(cluster)
        cluster += 1
    dfs.reset_index(inplace=True)
    i = 0
    while i < (len(dfs.cluster.unique())-1):
        if dfs.loc[[i]].cluster.tolist()[0] in delete_clusters:
            dfs.drop(i,0,inplace=True)
        i += 1
    dfs.set_index('id',inplace=True)

    # Create list of lists of song ids
    i=0
    recs = [0]*len(dfs.groupby('cluster').count())
    while i<len(dfs.groupby('cluster').count()):
        recs[i] = dfs.loc[dfs['cluster'] == i].index.to_list()
        i+=1

    recs = [ele for ele in recs if ele != []] 

    # Adjust list for clusters so that each cluster has a maximum of 5 seed songs
    for i in range(len(recs)):
        if len(recs[i]) > 5:
            recs[i] = random.sample(recs[i], 5)
    
    rec_weights = []
    for cluster in recs:
        total_weight = 0
        for song in cluster:
            info = dfs.loc[song]
            w = info.loc['weight']
            total_weight += w
        rec_weights.append(total_weight)

    return [(recs[i], rec_weights[i]) for i in range(len(recs))]


def get_shared_playlist(name1, name2):
    network = lastfm.get_network(name1)
    # use network to retrive User objects
    usr1 = network.get_user(name1)
    usr2 = network.get_user(name2)

    # collect the top tracks form 
    tracks1 = []
    tracks2 = []
    try:
        tracks1 = usr1.get_top_tracks(limit = NUM_SONGS_FROM_USERS, period=pylast.PERIOD_OVERALL)
    except:
        tracks1 = []
    if not tracks1:
        return f"Error: Could not find user \"{name1}\" in last.fm", True
    try:
        tracks2 = usr2.get_top_tracks(limit = NUM_SONGS_FROM_USERS, period=pylast.PERIOD_OVERALL)
    except:
        tracks2 = []
    if not tracks2:
        return f"Error: Could not find user \"{name2}\" in last.fm", True
    
    df1 = get_df(tracks1)
    df2 = get_df(tracks2)
    # normalize weights to an average of 1
    df1.weight *= 1 / np.mean(df1.weight)
    df2.weight *= 1 / np.mean(df2.weight)
    all_songs = pd.concat([df1, df2])
    all_songs.reset_index(drop=True, inplace=True)

    dfs = spotify.add_features(df1, df2)
    # all_songs['id'] = dfs.loc['id']
    
    recs = get_list_of_recs(dfs, all_songs)

    recommendations, num_recs = spotify.get_recs(recs, 30)
    recommendations_converted = [
        pd.json_normalize(rec, record_path='tracks').id.tolist()
        for rec in recommendations
    ]

    no_integers = [x for x in recommendations_converted if not isinstance(x, int)]
    recommendations_converted = [item for elem in no_integers for item in elem]

    return recommendations_converted, False

# for testing purposes
if __name__  == "__main__":
    name1 = input("User 1's last.fm username: ")
    name2 = input("User 2's last.fm username: ")
    print(get_shared_playlist(name1, name2))