# GET /api/<>/search?track_name=T&artist_name=A&album_name=B HTTP/1.1
# Host: lrclib.net

# spotify_refresh_token="AQCxbgwXDOwAXdrejNx3zB4tUt2iNK5Y_psGiScq4cBrKLyOHYPlsoWWED20l7VgzWvMcNlFLtsXt5gBxPK-R1D3HKFuQTZDNieHmtC6ZyJ3ut9xi-Y2s50INjj5exWDVgI"
# spotify_sp_dc_cookie="AQD7EPnLVh5_bHU668oMBvTSCvF7xRevTeMAFdiDfHrTZ_UyBtginl74FyzaQoS1CpKYXfS9pDbZwEx0n6g7e3D5SC37clakNHjWXTAYS6qjJdOFVN-CY0iZR98DNsWhVvaym6UY9q3cCvyeBaaDFrg9PUiVSXCY"

# spheader={}
# spotify_access_token=""
# lyrics_token=""

# def spotify_token():
#     global spheader, spotify_access_token, lyrics_token
#     spotify_access_token=requests.post('https://accounts.spotify.com/api/token',data=f"grant_type=refresh_token&refresh_token={spotify_refresh_token}",headers={"Authorization":"Basic YmYxZDcyZWYxY2E1NGVhMTg0M2QyOWI3NGE1ZTc0MDA6NjkzNjEzNWQ4M2FiNDlhMmI5ODhjYmRkZjVkYmVmY2U=","Content-Type":"application/x-www-form-urlencoded"}).json()['access_token']
#     spheader={"Authorization":f"Bearer {spotify_access_token}"}
#     r=requests.get('https://open.spotify.com/get_access_token?reason=transport&productType=web_player',headers={"Cookie":f"sp_dc={spotify_sp_dc_cookie}"})
#     if r.status_code==401:
#         print('spotify sc-dc cookie expired!')
#     else:lyrics_token= r.json()['accessToken']

# def add_to_spotify(name):
#     r=requests.get(f'https://api.spotify.com/v1/search?q={urllib.parse.quote(name)}&type=track&limit=1',headers=spheader).json()

# def getLyrics(fid,name,tid):
#     r=requests.get("https://api.textyl.co/api/lyrics?q="+name)
#     if r.status_code==200:
#         with open(f'{fid}.json','w') as f:
#             f.write(r.text)
#         return True

#     if tid:
#         r=requests.get(f'https://spclient.wg.spotify.com/color-lyrics/v2/track/{tid}?format=json&market=from_token',headers={"Authorization":f"Bearer {lyrics_token}","App-platform": "WebPlayer"})
#         if r.status_code==200:
#             print('spotify lyrics found!')
#             lydata=[]
#             r=r.json()
#             for line in r['lyrics']['lines']:
#                 sec=int(line['startTimeMs'])//1000
#                 lydata.append({'seconds':sec,'lyrics':line['words']})
#             with open(f'{fid}.json','w') as f:
#                 json.dump(lydata,f)
#             return True
#     return False
def get_song_lyrics(q):
    return "[00:2.51] How many times will they tell me \"no\"?\n[00:5.13] How many times will they shoot me down and close the door?\n[00:15.91] How"

def get_lyrics(q):
    return "[00:2.51] How many times will they tell me \"no\"?\n[00:5.13] How many times will they shoot me down and close the door?\n[00:15.91] How"
