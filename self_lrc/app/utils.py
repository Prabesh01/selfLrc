import requests
import re
from .spotify import * 

def lrclib_search(t, r):
    r=requests.get("https://lrclib.net/api/get?track_name="+t+"&artist_name="+r+"&album_name=")
    r=r.json()
    if 'syncedLyrics' in r:
        return r['id'], r['syncedLyrics']
    else:
        return None, None

def search_spotify(t, r):
    lid = spotify_seach_song(t + " " + r)
    if lid:
        lrc = get_spotify_Lyrics(lid)
        if not lrc:
            return None, None
        return lid, lrc
    else: return None, None


def search_lyrics(track, artist):
    lid, lrc = lrclib_search(track, artist)
    if lid and lrc:
            return 2, lid, lrc
    lid, lrc = search_spotify(track, artist)
    if lid:
        return 1, lid, lrc
    return False, None, "NotFound"

def get_local_lyrics(song):
    if song.lyrics_db!=0  and not song.lyrics_db: 
        return "NotFound"
    lid= song.lyrics_id
    custom_lyrics = song.custom_lyrics
    if song.custom_lyrics and not song.custom_lyrics.strip(): custom_lyrics = "NotFound"
    if lid==0:
        return custom_lyrics
    if not lid:
        title=song.title
        if song.updated_title: title=song.updated_title
        title_pattern = r'^(.*?) - (.*?)$'
        match = re.match(title_pattern, title)
        if match:
            name, artist = match.groups()
            lrc=update_lyrics(name, artist, song)
            return lrc
        #     _, _, x = search_lyrics(name.strip(), artist.strip(), album.strip())
        #     return x
        else:
            return custom_lyrics
    ldb=song.lyrics_db
    if ldb==2:
        return requests.get(f"https://lrclib.net/api/get/{lid}").json()['syncedLyrics']
    elif ldb==1:
        return get_spotify_Lyrics(song.lyrics_id)
    else:
        return custom_lyrics

def get_lyrics(track, artist, user):
    from .models import Song

    song=Song.objects.filter(title=f"{track} - {artist}")
    if song:
        return get_local_lyrics(song.first())
    else:
        lbd, lid, lrc = search_lyrics(track, artist)
        if lrc=="tryAgain":
            return lrc
        if lbd:
            Song.objects.create(user=user, title=f"{track} - {artist}", lyrics_id=lid, lyrics_db=lbd)
        else:
            Song.objects.create(user=user, title=f"{track} - {artist}")
        return lrc
    
def update_lyrics(track, artist, song):
    lbd, lid, lrc = search_lyrics(track, artist)
    if lbd:
        song.lyrics_id=lid
        song.lyrics_db=lbd
    else:
        song.lyrics_id=None
        song.lyrics_db=None
    song.save()
    return lrc