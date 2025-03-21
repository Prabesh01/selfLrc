# Self-hosted lyrics api for poweramp.
- Fetches lyrics from lrclib.net and spotify.
- Manage your lyrics from django admin panel.

### Setup
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
 - /api/get?q=''
 - /api/get?track_name=&artist_name=&album_name=

 ### Poweramp lyrics
 - clone: https://github.com/abhishekabhi789/LyricsForPoweramp.git
 - Edit `/app/src/main/java/io/github/abhishekabhi789/lyricsforpoweramp/helpers/LrclibApiHelper.kt` and set `API_BASE_URL` to the `https://<url-to-access-your-selflrc-django-website>/<username>/api`
 - Create apk with `gradle assembleDebug`
 - install the apk made in `app/build/outputs/apk/debug/Lyrics4Poweramp-vx.x-debug.apk`
 - enjoy enhanced lyrics in poweramp with this plugin.
 