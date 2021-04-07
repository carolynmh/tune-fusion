import pylast
from config import LASTFM_API_KEY, LASTFM_API_SECRET

# Type help(pylast.LastFMNetwork) or help(pylast) in a Python interpreter
# to get more help about anything and see examples of how it works
# https://www.last.fm/api


def get_network(username, password_hash=None):
    # In order to perform a write operation you need to authenticate yourself
    # password_hash = pylast.md5(PASSWORD)
    if password_hash:
        return pylast.LastFMNetwork(
            api_key=LASTFM_API_KEY,
            api_secret=LASTFM_API_SECRET,
            username=username,
            password_hash=password_hash,
        )
    return pylast.LastFMNetwork(
        api_key=LASTFM_API_KEY,
        api_secret=LASTFM_API_SECRET,
        username=username,
    )


