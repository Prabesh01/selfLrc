# Self-hosted lyrics api.
- Fetches lyrics from lrclib.net and spotify.
- Manage your lyrics from django admin panel.
- Focused for poweramp. supports SongSync, FastLyrics and harmonoid as well.

### See it in action
- Web:
  - https://lrc.cote.ws/demo/api/search?q=bistarai%20bistarai
  - https://lrc.cote.ws/demo/api/search?track_name=exile&artist_name=taylor&album_name=folklore
  - https://lrc.cote.ws/demo/api/get?track_name=question&artist_name=Rhett%20Miller&album_name=
- App:
  - Download latest release from https://github.com/Prabesh01/selfLrc/releases/latest
  - Login as demo user in https://lrc.cote.ws/ to view dashboard. 

### Self-Host
- Copy .env.examples to .env and fill required values
- python manage.py makemigrations app
- python manage.py migrate
- python manage.py runserver
Login as `admin`:`pass` on http://127.0.0.1:8000/

### Usage
- Create Users with `allow` group and `staff` role.
- These user can now login to django admin panel and manage their songs lyrics.
- These users can now fetch lyrics from
 - /api/search?q=''
 - /api/search?track_name=&artist_name=&album_name=
 - /api/get?track_name=&artist_name=&album_name=
 - /api/get/xxx:id

 ### modify lyrics apps to use selfLrc API

_Since selfLrc's API uses exact same format as lrclib, simply substituting the api url in apps will make the app fetch lyrics from selfLrc instead of lrclib._

 ## lyrics for Poweramp
 - clone: https://github.com/abhishekabhi789/LyricsForPoweramp.git
 - Edit `app/src/main/java/io/github/abhishekabhi789/lyricsforpoweramp/helpers/LrclibApiHelper.kt` and set `API_BASE_URL` to the `https://<url-to-access-your-selflrc-django-website>/<username>/api`
 - Create apk with `gradle assembleDebug`
 - install the apk made in `app/build/outputs/apk/debug/Lyrics4Poweramp-vx.x-debug.apk`
 - enjoy enhanced lyrics in poweramp with this plugin.
 
 ## SongSync
 - clone: https://github.com/Lambada10/SongSync.git
 - Edit `app/src/main/java/pl/lambada/songsync/data/remote/lyrics_providers/others/LRCLibAPI.kt` and set `baseURL` tp `https://<url-to-access-your-selflrc-django-website>/<username>/api/` 
 - Create apk with .... [same as above]

 ## FastLyrics
 - clone: https://github.com/teccheck/FastLyrics
 - Edit `app/src/main/java/io/github/teccheck/fastlyrics/api/provider/LrcLib.kt` and set `baseURL` tp `https://<url-to-access-your-selflrc-django-website>/<username>/api/` 
 - Create apk with .... [same as above]
