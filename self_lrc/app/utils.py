import httpx
import re
from app.spotify import SpotifyTokenManager
from asgiref.sync import sync_to_async
from app.models import Song

spotify = None

async def get_spotify_instance():
    global spotify
    if spotify is None:
        spotify = await SpotifyTokenManager.create()
    return spotify

async def close_spotify_instance():
    global spotify
    if spotify is not None:
        await spotify.close()
        spotify = None

@sync_to_async
def get_song_by_title(title):
    return Song.objects.filter(title=title).first()

@sync_to_async
def create_song(user, title, lyrics_id=None, lyrics_db=None):    
    if lyrics_id and lyrics_db:
        return Song.objects.create(user=user, title=title, lyrics_id=lyrics_id, lyrics_db=lyrics_db)
    else:
        return Song.objects.create(user=user, title=title)


async def lrclib_search(t, r):
    async with httpx.AsyncClient(timeout=10.0) as client:
        response=await client.get("https://lrclib.net/api/get?track_name="+t+"&artist_name="+r+"&album_name=")
        r = response.json()
        if 'syncedLyrics' in r:
            return r['id'], r['syncedLyrics']
        else:
            return None, None

async def search_spotify(t, r):
    spotify = await get_spotify_instance()
    try:
        lid = await spotify.spotify_search_song(t + " " + r)
        if lid:
            lrc = await spotify.get_spotify_lyrics(lid)
        
            if not lrc:
                return None, None
            return lid, lrc
        else: return None, None
    finally: await close_spotify_instance()

async def search_lyrics(track, artist):
    lid, lrc = await lrclib_search(track, artist)
    if lid and lrc:
            return 2, lid, lrc
    lid, lrc = await search_spotify(track, artist)
    if lid:
        return 1, lid, lrc
    return False, None, "NotFound"

async def get_local_lyrics(song):
    if song.lyrics_db!=0  and not song.lyrics_db: 
        return "NotFound"
    lid= song.lyrics_id
    custom_lyrics = song.custom_lyrics
    if not custom_lyrics or  (custom_lyrics and not custom_lyrics.strip()): custom_lyrics = "NotFound"
    if lid==0:
        return custom_lyrics
    if not lid:
        title=song.title
        if song.updated_title: title=song.updated_title
        title_pattern = r'^(.*?) - (.*?)$'
        match = re.match(title_pattern, title)
        if match:
            name, artist = match.groups()
            lrc=await update_lyrics(name, artist, song)
            return lrc
        #     _, _, x = search_lyrics(name.strip(), artist.strip(), album.strip())
        #     return x
        else:
            return custom_lyrics
    ldb=song.lyrics_db
    if ldb==2:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(f"https://lrclib.net/api/get/{lid}")
            return response.json()['syncedLyrics']    
    elif ldb==1:
        spotify = await get_spotify_instance()
        try: return await spotify.get_spotify_lyrics(song.lyrics_id)
        finally: await close_spotify_instance()
    else:
        return custom_lyrics

async def get_lyrics(track, artist, user):
    song=await get_song_by_title(f"{track} - {artist}")
    if song:
        return await get_local_lyrics(song)
    else:
        lbd, lid, lrc = await search_lyrics(track, artist)
        if lrc=="tryAgain":
            return lrc
        if lbd:
            await create_song(user, f"{track} - {artist}", lid, lbd)
        else:
            await create_song(user, f"{track} - {artist}")
        return lrc
    
async def update_lyrics(track, artist, song):
    lbd, lid, lrc = await search_lyrics(track, artist)
    @sync_to_async
    def update_song_fields():
        if lbd:
            song.lyrics_id=lid
            song.lyrics_db=lbd
        else:
            song.lyrics_id=None
            song.lyrics_db=None
        song.save()
    if lrc!="tryAgain": await update_song_fields()

    return lrc