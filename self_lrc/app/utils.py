import requests
from .models import Song
import re
# GET /api/<>/search?track_name=T&artist_name=A&album_name=B HTTP/1.1
# Host: lrclib.net

def lrclib_search(t, r, l):
    r=requests.get("https://lrclib.net/api/get?track_name="+t+"&artist_name="+r+"&album_name="+l)
    r=r.json()
    if 'syncedLyrics' in r:
        return r['id'], r['syncedLyrics']
    else:
        return None, None

def spotify_search(t, r, l):
    pass


def search_lyrics(track, artist, album):
    print('#############################################')
    lid, lrc = lrclib_search(track, artist, album)
    if lid:
        return 2, lid, lrc
    # lid, lrc = spotify_search(track, artist, album)
    # if lid:
    #     return 1, lid, lrc
    return False, None, "[00:10.00] :(\n[00:15.00] Not Found"
    

def get_local_lyrics(song):
    if not song.lyrics_db: return "[00:10.00] :(\n[00:15.00] Not Found"
    lid= song.lyrics_id
    if not lid:
        title=song.title
        if song.updated_title: title=song.updated_title
        title_pattern = r'^(.*?) - (.*?) \[(.*?)\]$'
        match = re.match(title_pattern, title)
        if match:
            name, artist, album = match.groups()
            lrc=update_lyrics(name, artist, album, song)
            return lrc
        #     _, _, x = search_lyrics(name.strip(), artist.strip(), album.strip())
        #     return x
        else:
            return song.custom_lyrics
    ldb=song.lyrics_db
    if ldb==0:
        return song.custom_lyrics
    elif ldb==2:
        return requests.get(f"https://lrclib.net/api/get/{lid}").json()['syncedLyrics']
    # elif ldb==1:
    #     pass


def get_lyrics(track, artist, album, user):
    song=Song.objects.filter(title=f"{track} - {artist} [{album}]")
    if song:
        return get_local_lyrics(song.first())
    else:
        lbd, lid, lrc = search_lyrics(track, artist, album)
        if lbd:
            Song.objects.create(user=user, title=f"{track} - {artist} [{album}]", lyrics_id=lid, lyrics_db=lbd)
        else:
            Song.objects.create(user=user, title=f"{track} - {artist} [{album}]")
        return lrc
    
def update_lyrics(track, artist, album, song):
    lbd, lid, lrc = search_lyrics(track, artist, album)
    if lbd:
        song.lyrics_id=lid
        song.lyrics_db=lbd
    else:
        song.lyrics_id=None
        song.lyrics_db=None
    song.save()
    return lrc