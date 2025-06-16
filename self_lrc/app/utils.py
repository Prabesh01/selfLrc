import httpx
import re
from app.spotify import SpotifyTokenManager
from asgiref.sync import sync_to_async
from app.models import Song
import asyncio
from .cryptographic_challenge_solver import CryptoChallengeSolver

from base64 import b64encode
from dotenv import load_dotenv
import os
from pathlib import Path
BASE_DIR = Path(__file__).resolve().parent.parent.parent
ENV_FILE = BASE_DIR / '.env'
load_dotenv(ENV_FILE)
ntfy_url=os.environ.get("ntfy_url")
ntfy_user=os.environ.get("ntfy_user")
ntfy_password=os.environ.get("ntfy_password")
credentials = f"{ntfy_user}:{ntfy_password}"
b64_credentials = b64encode(credentials.encode('utf-8')).decode('utf-8')

import os
num_threads = os.cpu_count() or 1

spotify = None
headers = {
    "User-Agent": "selfLrc (https://github.com/Prabesh01/selfLrc)"
}

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

async def lrclib_search(t, r, a=""):
    async with httpx.AsyncClient(timeout=10.0) as client:
        response=await client.get("https://lrclib.net/api/get?track_name="+t+"&artist_name="+r+"&album_name="+a, headers=headers)
        r = response.json()
        if 'syncedLyrics' in r:
            return r['id'], r['syncedLyrics']
        else:
            return None, None

async def convert_to_plain_lrc(lrc):
    plain_lyrics = ""
    try:
        lines = lrc.split("\n")
        for line in lines:
            if not line: continue
            time, words = line.split("]", 1)
            plain_lyrics += f"{words}\n"
        return plain_lyrics
    except:
        return plain_lyrics

async def contribute_lyrics_to_lrclib(lid, lrc):
    spotify = await get_spotify_instance()
    trackName, artistName, albumName, duration = await spotify.get_track_info(lid)
    await close_spotify_instance()

    if not trackName: return

    lrclib_lid, lrclib_lrc = await lrclib_search(trackName, artistName, albumName)
    if lrclib_lid and lrclib_lrc: return

    plainLyrics = await convert_to_plain_lrc(lrc)
    payload = { "trackName": trackName, "artistName": artistName, "albumName": albumName, "duration": duration, "plainLyrics": plainLyrics.strip(), "syncedLyrics": lrc}

    async with httpx.AsyncClient(timeout=10.0) as client:
        response=await client.post("https://lrclib.net/api/request-challenge", headers=headers)
        prefix,target = response.json().values()

    nonce = CryptoChallengeSolver.solve(
        prefix, target, num_threads=num_threads
    )
    con_headers = headers.copy()
    con_headers["X-Publish-Token"]=f"{prefix}:{nonce}"

    async with httpx.AsyncClient(timeout=10.0) as client:
        response=await client.post("https://lrclib.net/api/publish", json=payload, headers=con_headers)
    if response.status_code!=200: return
    async with httpx.AsyncClient(timeout=10.0) as client:
        await client.post(ntfy_url, data=f"{trackName} by {artistName}".encode(encoding='utf-8'), headers={"Authorization":"Basic "+b64_credentials, "Title": "Contributed to lrclib.net"})

async def search_spotify(t, r):
    spotify = await get_spotify_instance()
    try:
        lid = await spotify.spotify_search_song(t + " " + r)
        if lid:
            lrc = await spotify.get_spotify_lyrics(lid)
        
            if not lrc:
                return None, None
            else:
                asyncio.create_task(contribute_lyrics_to_lrclib(lid,lrc))
                # await contribute_lyrics_to_lrclib(lid,lrc)
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
            response = await client.get(f"https://lrclib.net/api/get/{lid}", headers=headers)
            return response.json()['syncedLyrics']    
    elif ldb==1:
        spotify = await get_spotify_instance()
        try: return await spotify.get_spotify_lyrics(song.lyrics_id)
        finally: await close_spotify_instance()
    else:
        return custom_lyrics

async def adjust_lyrics(lyrics, delay):
    # lyrics fomatt:
    # f"[{minutes:02}:{seconds:02}.{int(fractional_seconds * 100):02}] {line['words']}\n"
    # speed or delay lyrics by x seconds
    if not delay: return lyrics
    try: delay = int(delay)
    except: return lyrics
    if delay==0: return lyrics
    try:
        lines = lyrics.split("\n")
        new_lyrics = ""
        for line in lines:
            if not line: continue
            time, words = line.split("]", 1)
            time = time[1:]
            minutes, seconds= time.split(":")
            seconds, ms = seconds.split(".")
            total_seconds = int(minutes)*60 + int(seconds) + delay
            minutes = total_seconds // 60
            seconds = total_seconds % 60
            new_lyrics += f"[{minutes:02}:{seconds:02}.{ms}] {words}\n"
        return new_lyrics
    except:
        return lyrics

async def get_lyrics(track, artist, user):
    song=await get_song_by_title(f"{track} - {artist}")
    if song:
        lrc = await get_local_lyrics(song)
        return await adjust_lyrics(lrc, song.delay)
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

async def validate_cookie(cookie):
    spotify = await get_spotify_instance()
    return await spotify.validate_spotify_cookie(cookie)
