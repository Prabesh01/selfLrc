import requests
import urllib

import os
from pathlib import Path
from dotenv import load_dotenv
import base64

import pyotp
import base64
import time

BASE_DIR = Path(__file__).resolve().parent.parent.parent
ENV_FILE = BASE_DIR / '.env'
load_dotenv(ENV_FILE)

spotify_refresh_token=os.environ.get("SPOTIFY_REFRESH_TOKEN")
spitify_sp_dc_cookie = os.environ.get("spitify_sp_dc_cookie")

spotify_access_token=""
lyrics_token=""

def generate_totp(server_time_seconds):
    secret_cipher = [12, 56, 76, 33, 88, 44, 88, 33, 78, 78, 11, 66, 22, 22, 55, 69, 54]

    processed = []
    for i, byte in enumerate(secret_cipher):
        processed.append(byte ^ (i % 33 + 9))

    processed_str = ''.join(str(x) for x in processed)
    utf8_bytes = processed_str.encode('utf-8')
    hex_str = utf8_bytes.hex()
    cleaned_hex = clean_hex(hex_str)
    secret_bytes = bytes.fromhex(cleaned_hex)
    secret_base32 = base64.b32encode(secret_bytes).decode('utf-8').rstrip('=')

    totp = pyotp.TOTP(secret_base32, interval=30, digits=6, digest='sha1')
    return totp.at(int(server_time_seconds))

def clean_hex(hex_str):
    valid_chars = '0123456789abcdefABCDEF'
    cleaned = ''.join(c for c in hex_str if c in valid_chars)

    if len(cleaned) % 2 != 0:
        cleaned = cleaned[:-1]

    return cleaned

def refresh_spotify_token():
    global spotify_access_token, lyrics_token
    spotify_access_token=requests.post('https://accounts.spotify.com/api/token',data=f"grant_type=refresh_token&refresh_token={spotify_refresh_token}",headers={"Authorization": f"Basic {base64.b64encode(f'{os.environ['spotify_client_id']}:{os.environ['spotify_client_secret']}'.encode()).decode()}","Content-Type":"application/x-www-form-urlencoded"}).json()['access_token']    

    server_time=requests.get('https://open.spotify.com/server-time').json()['serverTime']

    totp = generate_totp(server_time)
    timestamp = int(time.time())

    r=requests.get(f'https://open.spotify.com/get_access_token?reason=transport&productType=web_player&totp={totp}&totpVer=5&totpServer={timestamp}',headers={"Cookie":f"sp_dc={spitify_sp_dc_cookie}"})
    if not 'accessToken' in r.json():
        lyrics_token = ''
    else: lyrics_token= r.json()['accessToken']

refresh_spotify_token()

def spotify_seach_song(name, i=True):
    r=requests.get(f'https://api.spotify.com/v1/search?q={urllib.parse.quote(name)}&type=track&limit=1',headers={"Authorization":f"Bearer {spotify_access_token}"}).json()
    if not 'tracks' in r:
        if i:
            refresh_spotify_token()
            return spotify_seach_song(name, False)
        else:
            print('spotify token  expired')
    else: return r['tracks']['items'][0]['id']

def get_spotify_Lyrics(tid,i=True):
    r=requests.get(f'https://spclient.wg.spotify.com/color-lyrics/v2/track/{tid}/?format=json&market=from_token',headers={"Authorization":f"Bearer {lyrics_token}","app-platform": "WebPlayer","User-Agent":"Mozilla/5.0"})
    if r.status_code==404:
        return None
    elif r.status_code==200:
        r=r.json()['lyrics']
        lines=r['lines']
        return parse_lyrics(lines)
    else: 
        if i:
            refresh_spotify_token()
            return get_spotify_Lyrics(tid, False)
        else:
            print('cookie expired')
            return 'tryAgain'

def parse_lyrics(lines):
    lyrics=''
    for line in lines:
        milliseconds = int(line['startTimeMs'])
        total_seconds = milliseconds / 1000  # Convert milliseconds to seconds
        minutes = int(total_seconds // 60)  # Get the number of minutes
        seconds = int(total_seconds % 60)    # Get the remaining seconds
        fractional_seconds = total_seconds - (minutes * 60 + seconds)  # Get fractional part        
        lyrics+=f"[{minutes:02}:{seconds:02}.{int(fractional_seconds * 100):02}] {line['words']}\n"
    return lyrics
