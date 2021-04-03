import lastfm
import pylast
import pandas as pd

# number of tracks from each user
N = 50

def get_shared_playlist(tracks1, tracks2):
    # create a dataframe for each user
    df1 = pd.DataFrame()
    df2 = pd.DataFrame()

    # collect info from track
    return []
    
def get_df(tracks):
    weights = []
    artists = []
    titles = []
    items = []
    for track in tracks:
        item = track.item
        weight = track.weight
        weights.append(weight)
        artists.append(item.artist.name)
        titles.append(item.title)
        # lastfm's "similar" only works on some tracks
        # similar = item.get_similar(limit=2)
        # print(item.title, similar)
        items.append(track.item)
    df = pd.DataFrame(
        {'artist': artists,
        'song': titles,
        'weight': weights,
        'item': items}
    )
    return df

if __name__  == "__main__":
    name1 = input("User 1's last.fm username: ")
    name2 = input("User 2's last.fm username: ")
    network = lastfm.get_network(name1)
    # use network to retrive User objects
    usr1 = network.get_user(name1)
    usr2 = network.get_user(name2)

    # collect the top tracks form 
    tracks1 = usr1.get_top_tracks(limit = N, period=pylast.PERIOD_OVERALL)
    tracks2 = usr2.get_top_tracks(limit = N, period=pylast.PERIOD_OVERALL)
    
    df1 = get_df(tracks1)
    df2 = get_df(tracks2)
    

    shared = get_shared_playlist(tracks1, tracks2)

    print(f"FUSED TUNES FOR {name1} AND {name2}")
    for i in range(len(shared)):
        print(f"{i:2d}: {shared[i]}")


    