import urllib
import os
import json
from pathlib import Path
from dotenv import load_dotenv, set_key
import base64
import pyotp
import time
import httpx

import asyncio

class SpotifyTokenManager:
    def __init__(self):
        BASE_DIR = Path(__file__).resolve().parent.parent.parent
        self.ENV_FILE = BASE_DIR / '.env'
        load_dotenv(self.ENV_FILE)
        
        self.cache_file = BASE_DIR / 'spotify_token_cache.json'
        
        self.refresh_token = os.environ.get("SPOTIFY_REFRESH_TOKEN")
        self.sp_dc_cookie = os.environ.get("spitify_sp_dc_cookie")
        self.client_id = os.environ.get("spotify_client_id")
        self.client_secret = os.environ.get("spotify_client_secret")
        
        self.state1=False
        self.state2=False
        self.state0=False

        self.spotify_access_token = ""
        self.lyrics_token = ""

        self.lock = asyncio.Lock()
        self.client = None

    @classmethod
    async def create(cls):
        instance = cls()
        await instance.initialize()
        return instance

    async def initialize(self):
        self.client = httpx.AsyncClient(timeout=10.0)
        await self._load_or_refresh_tokens()

    async def _load_or_refresh_tokens(self):
        if not await self._load_tokens_from_cache():
            print("Cached Tokens expired! Refreshing both tokens...")
            await self.refresh_spotify_token()
            await self.refresh_spotify_lrc_token()
    
    async def _load_tokens_from_cache(self):
        try:
            if not self.cache_file.exists():
                return False
                
            with open(self.cache_file, 'r') as f:
                cache = json.load(f)
                                
            self.spotify_access_token = cache.get('spotify_access_token', '')
            self.lyrics_token = cache.get('lyrics_token', '')
            
            return bool(self.spotify_access_token and self.lyrics_token)
        except Exception as e:
            print(f"Error loading from cache: {e}")
            return False
    
    async def _save_tokens_to_cache(self):        
        cache_data = {
            'spotify_access_token': self.spotify_access_token,
            'lyrics_token': self.lyrics_token,
        }
        
        try:
            with open(self.cache_file, 'w') as f:
                json.dump(cache_data, f)
        except Exception as e:
            print(f"Error saving to cache: {e}")
    
    def generate_totp(self, server_time_seconds):
        secret_cipher = [12, 56, 76, 33, 88, 44, 88, 33, 78, 78, 11, 66, 22, 22, 55, 69, 54]

        processed = []
        for i, byte in enumerate(secret_cipher):
            processed.append(byte ^ (i % 33 + 9))

        processed_str = ''.join(str(x) for x in processed)
        utf8_bytes = processed_str.encode('utf-8')
        hex_str = utf8_bytes.hex()
        cleaned_hex = self._clean_hex(hex_str)
        secret_bytes = bytes.fromhex(cleaned_hex)
        secret_base32 = base64.b32encode(secret_bytes).decode('utf-8').rstrip('=')

        totp = pyotp.TOTP(secret_base32, interval=30, digits=6, digest='sha1')
        return totp.at(int(server_time_seconds))

    def _clean_hex(self, hex_str):
        valid_chars = '0123456789abcdefABCDEF'
        cleaned = ''.join(c for c in hex_str if c in valid_chars)

        if len(cleaned) % 2 != 0:
            cleaned = cleaned[:-1]

        return cleaned

    async def refresh_spotify_token(self):
        async with self.lock:
            if self.state1:
                return False
            self.state1 = True
        print('Refreshing Spotify tokens...')
        try:
            auth_header = base64.b64encode(f'{self.client_id}:{self.client_secret}'.encode()).decode()
            response = await self.client.post(
                'https://accounts.spotify.com/api/token',
                data=f"grant_type=refresh_token&refresh_token={self.refresh_token}",
                headers={
                    "Authorization": f"Basic {auth_header}",
                    "Content-Type": "application/x-www-form-urlencoded"
                }
            )
            async with self.lock:
                self.state1 = False
            if response.status_code == 200:
                data = response.json()

                self.spotify_access_token = data['access_token']
                await self._save_tokens_to_cache()
                return True

            else:
                print(f"Failed to refresh Spotify token: {response.status_code}")
                return False
        except Exception as e:
            print(f"Error refreshing Spotify token: {e}")
            async with self.lock:
                self.state1 = False
            return False

    async def validate_spotify_cookie(self,cookie):
        if cookie==self.sp_dc_cookie: return True
        async with self.lock:
            if self.state0:
                return False
            self.state0 = True
        print('Validating user provided cookie...')
        try:
            server_time_response = await self.client.get('https://open.spotify.com/api/server-time')

            server_time = server_time_response.json()['serverTime']
            totp = self.generate_totp(server_time)
            timestamp = int(time.time())

            response = await self.client.get(
                f'https://open.spotify.com/get_access_token?reason=transport&productType=web_player&totp={totp}&totpVer=5&totpServer={timestamp}',
                headers={"Cookie": f"sp_dc={cookie}"},
                timeout=5
            )

            async with self.lock: self.state0=False
            if response.status_code == 200 and 'accessToken' in response.json():
                self.sp_dc_cookie=cookie
                set_key(self.ENV_FILE, "spitify_sp_dc_cookie", cookie)
                self.lyrics_token = response.json()['accessToken']
                await self._save_tokens_to_cache()
                return True
            else: return False
        except Exception as e:
            print(f"Error validate sp_dc cookie: {e}")
            async with self.lock: self.state0=False
            return False

    async def refresh_spotify_lrc_token(self):
        async with self.lock:
            if self.state2:
                return False
            self.state2 = True
        print('Refreshing lyrics tokens...')
        try:
            server_time_response = await self.client.get('https://open.spotify.com/api/server-time')
            server_time = server_time_response.json()['serverTime']
            totp = self.generate_totp(server_time)
            timestamp = int(time.time())
            
            response = await self.client.get(
                f'https://open.spotify.com/api/token?reason=transport&productType=web_player&totp={totp}&totpVer=5&totpServer={timestamp}',
                headers={"Cookie": f"sp_dc={self.sp_dc_cookie}"},
                timeout=5
            )
            async with self.lock: self.state2=False
            if response.status_code == 200 and 'accessToken' in response.json():
                self.lyrics_token = response.json()['accessToken']
                await self._save_tokens_to_cache()
                return True
            else:
                print(f"Failed to refresh lyrics token: {response.status_code}")
                return False
        except Exception as e:
            print(f"Error refreshing lyrics token: {e}")
            async with self.lock: self.state2=False
            return False
        
    async def spotify_search_song(self, name, re=True):
        """Search for a song on Spotify and return its ID"""
        try:
            response = await self.client.get(
                f'https://api.spotify.com/v1/search?q={urllib.parse.quote(name)}&type=track&limit=1',
                timeout=5,
                headers={"Authorization": f"Bearer {self.spotify_access_token}"}
            )
            data = response.json()
            
            if not 'tracks' in data:
                if re:
                    refresh_success = await self.refresh_spotify_token()
                    if refresh_success:
                        data = await self.spotify_search_song(name, False)
                        return data
                    else: return 'tryAgain'
                return None
            
            return data['tracks']['items'][0]['id']
        except Exception as e:
            print(f"Error searching for song: {e} {type(e)}")
            return "tryAgain"

    async def get_spotify_lyrics(self, track_id, re=True):
        """Get lyrics for a Spotify track by ID"""
        if track_id=='tryAgain': return track_id
        try:
            response = await self.client.get(
                f'https://spclient.wg.spotify.com/color-lyrics/v2/track/{track_id}/?format=json&market=from_token',
                timeout=5,
                headers={
                    "Authorization": f"Bearer {self.lyrics_token}",
                    "app-platform": "WebPlayer",
                    "User-Agent": "Mozilla/5.0"
                }
            )
            # Check if token is expired
            if response.status_code == 401:
                if re:
                    refresh_success = await self.refresh_spotify_lrc_token()
                    if refresh_success: 
                        data = await self.get_spotify_lyrics(track_id, False)
                        return data
                return 'tryAgain'
            
            if response.status_code == 200:
                lyrics_data = response.json()['lyrics']
                lines = lyrics_data['lines']
                return self._parse_lyrics(lines)
            else:
                return None
                
        except Exception as e:
            print(f"Error getting lyrics: {e}, Type: {type(e)}")
            return 'tryAgain'

    def _parse_lyrics(self, lines):
        """Parse lyrics lines into a formatted string with timestamps"""
        lyrics = ''
        for line in lines:
            milliseconds = int(line['startTimeMs'])
            total_seconds = milliseconds / 1000
            minutes = int(total_seconds // 60)
            seconds = int(total_seconds % 60)
            fractional_seconds = total_seconds - (minutes * 60 + seconds)
            lyrics += f"[{minutes:02}:{seconds:02}.{int(fractional_seconds * 100):02}] {line['words']}\n"
        return lyrics

    async def close(self):
        await self.client.aclose()
