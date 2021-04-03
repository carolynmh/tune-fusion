import lastfm
import pylast


if __name__  == "__main__":
    name1 = input("User 1's last.fm username: ")
    name2 = input("User 2's last.fm username: ")
    network = lastfm.get_network(name1)
    # use network to retrive User objects
    usr1 = network.get_user(name1)
    usr2 = network.get_user(name2)

    #
    tracks1 = usr1.get_top_tracks(period=pylast.PERIOD_OVERALL)
    tracks2 = usr2.get_top_tracks(period=pylast.PERIOD_OVERALL)

    