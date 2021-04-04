from spotipy.client import Spotify
import lastfm
import pylast
import pandas as pd
import spotify
from sklearn.cluster import KMeans
from sklearn.preprocessing import MinMaxScaler
from sklearn.decomposition import PCA 
import random

# number of tracks from each user
N = 32

def get_shared_playlist(tracks1, tracks2):
    # create a dataframe for each user
    df1 = pd.DataFrame()
    df2 = pd.DataFrame()

    # collect info from track
    return []
    
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
        'popularity': popularities
    })
    return df

def get_shared_playlist(name1, name2):
    network = lastfm.get_network(name1)
    # use network to retrive User objects
    usr1 = network.get_user(name1)
    usr2 = network.get_user(name2)

    # collect the top tracks form 
    tracks1 = usr1.get_top_tracks(limit = N, period=pylast.PERIOD_OVERALL)
    tracks2 = usr2.get_top_tracks(limit = N, period=pylast.PERIOD_OVERALL)
    
    df1 = get_df(tracks1)
    df2 = get_df(tracks2)
    all_songs = pd.concat([df1, df2])
    all_songs.reset_index(drop=True, inplace=True)

    dfs = spotify.add_features(df1, df2)

    
    columns = ['danceability','energy','speechiness','acousticness','valence','tempo']
    scaler = MinMaxScaler()
    scaler.fit(dfs[columns])
    dfs[columns] = scaler.transform(dfs[columns])
    print(dfs.head())

    clusters = 2
    kmeans = KMeans(n_clusters=clusters)
    kmeans.fit(dfs)
    pca = PCA(3) 
    pca.fit(dfs)   
    pca_data = pd.DataFrame(pca.transform(dfs))
    scaler = MinMaxScaler()
    scaled = scaler.fit_transform(dfs)
    y_kmeans = kmeans.fit_predict(scaled)
    dfs['cluster'] = y_kmeans
    dfs['artist'] = all_songs.artist.tolist()
    dfs['title'] = all_songs.song.tolist()
    
    # remove clusters with only one song in them
    delete_clusters = []
    cluster = 0
    while cluster < (len(dfs.cluster.unique())-1):
        if dfs.groupby('cluster').count().loc[cluster].danceability == 1:
            delete_clusters.append(cluster)
        cluster += 1
    dfs.reset_index(inplace=True)
    i = 0
    while i < (len(dfs.cluster.unique())-1):
        if dfs.loc[[i]].cluster.tolist()[0] in delete_clusters:
            dfs.drop(i,0,inplace=True)
        i+=1
    dfs.set_index('id',inplace=True)

    # Create list of lists of song ids to put into recommendation function
    i=0
    list_of_recs = [0]*len(dfs.groupby('cluster').count())
    while i<len(dfs.groupby('cluster').count()):
        list_of_recs[i] = dfs.loc[dfs['cluster'] == i].index.to_list()
        i+=1

    list_of_recs = [ele for ele in list_of_recs if ele != []] 
    len(list_of_recs)

    # Adjust list for clusters so that each cluster has a maximum of 5 seed songs
    j = 0
    adj_list_of_recs = [0]*len(list_of_recs)
    while j<len(list_of_recs):
        if 0 < len(list_of_recs[j]) < 6:
            adj_list_of_recs[j] = list_of_recs[j]
        elif len(list_of_recs[j]) > 5:
            adj_list_of_recs[j] = random.sample(list_of_recs[j], 5)
        j += 1

    len(adj_list_of_recs)

    list_of_recommendations = spotify.get_recs(list_of_recs, adj_list_of_recs)
    list_of_recommendations_converted = [0]*len(list_of_recs)

    l = 0
    while l < len(list_of_recs):
        list_of_recommendations_converted.append(pd.json_normalize(list_of_recommendations[l], record_path='tracks').id.tolist())
        l += 1

    no_integers = [x for x in list_of_recommendations_converted if not isinstance(x, int)]
    list_of_recommendations_converted = [item for elem in no_integers for item in elem]

    return list_of_recommendations_converted


if __name__  == "__main__":
    name1 = input("User 1's last.fm username: ")
    name2 = input("User 2's last.fm username: ")
    print(get_shared_playlist(name1, name2))