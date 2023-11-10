import json
from urllib.parse import urlencode
import requests
import authtoken
from flask import session

token = authtoken.get_token()
user_id = session["uid"] #this should be in authtoken, specified for each user

def whothisuser(token, user_id):
    url = f"https://api.spotify.com/v1/users/{user_id}/"
    headers = authtoken.get_auth_header(token)
    result = requests.get(url, headers=headers)
    
    json_result = json.loads(result.content)['display_name']
    return json_result

print()
print(whothisuser(token,user_id)) #prints my name

def createplaylist(token, user_id):
    
    url = f"https://api.spotify.com/v1/users/{user_id}/playlists"

    headers = {"Authorization": "Bearer " + token, "Content-Type": "application/json"} #or token
    
    data = json.dumps({"name": "New API Playlist"})
    
    result = requests.post(url, headers=headers, data=data)
    
    json_result = json.loads(result.content)
    
    playlist_id = json_result["id"]
    return playlist_id

def get_uri_for_podcast(token, podcast_name):
    url = "https://api.spotify.com/v1/search"
    headers = authtoken.get_auth_header(token)
    query = f"?q={podcast_name}&type=show&limit=1"
    query_url = url + query 
    result = requests.get(query_url, headers=headers)
    json_result = json.loads(result.content)
    if len(json_result) == 0:
        print("not artist with this name exists")
        return None
    json_result = json_result["shows"]["items"]
    uri = json_result[0]["id"]
    return uri

def get_podcast_by_artists(token, id):
    url = f"https://api.spotify.com/v1/shows/{id}/episodes?limit=1"
    headers = authtoken.get_auth_header(token)
    result = requests.get(url,headers=headers)
    json_result = json.loads(result.content)
    json_result = json_result["items"]
    uri = json_result[0]["uri"] #most recent podcast is at the top
    return uri

#playlist_id = createplaylist(token, user_id)
#uri=get_podcast_by_artists(token,get_uri_for_podcast(token,'Radio Headspace'))

def get_spotify_dailydrive(token):
    url = "https://api.spotify.com/v1/search"
    headers = authtoken.get_auth_header(token)
    query = f"?q='Daily Drive'&type=playlist&limit=1"
    query_url = url + query 
    result = requests.get(query_url, headers=headers)
    json_result = json.loads(result.content)
    if len(json_result) == 0:
        print("not artist with this name exists")
        return None
    json_result = json_result["playlists"]["items"]
    uri = json_result[0]["id"]
    return uri


def get_spotify_dd_opening(token, playlist_id):
    url = f"https://api.spotify.com/v1/playlists/{playlist_id}/tracks?offset=0&limit2"
    headers = authtoken.get_auth_header(token)
    result = requests.get(url, headers=headers)
    json_result = json.loads(result.content)
    json_result = json_result["items"]
    uri = json_result[0]["track"]["uri"]
    return uri
#daily drive opening track(changes each day)




#for idx, playlist in enumerate(playlists):
#   print(f"{idx + 1}. {playlist['name']}")

def populate_playlist(playlist_id,uri):
    url = f"https://api.spotify.com/v1/playlists/{playlist_id}/tracks"

    headers = {"Authorization": "Bearer " + token, "Content-Type": "application/json"} #or token
    #we will do get-uri for a track
    data = json.dumps({
        "uris": [
            uri
            ]
        })
    
    result = requests.post(url, headers=headers, data=data)
    
    json_result = json.loads(result.content)
    
    #playlist_id = json_result["id"]
    return playlist_id

playlist_id=get_spotify_dailydrive(token)
uri=get_spotify_dd_opening(token, playlist_id)

playlist_id=createplaylist(token,user_id)
print(populate_playlist(playlist_id,uri))


#print(populate_playlist(playlist_id,uri))

#for idx, items in enumerate(shows):
#   print(f"{idx + 1}. {items[0]}")


#then search for most recent episode, and get it's URI/ID, then add it to the playlist via URI
#i'll want to append these uri's
#make it to where I can choose what playlist i want daily drive to mix news and music with (it will have to randomize a set of songs from said playlist or i can just copy daily drive for now)
#create a text file for what News Stations I want it to play
#do a for loop. for every 3 songs, throw in a podcast.



#token = authtoken.get_token()
#result = search_for_artist(token, "AC/DC")
#artist_id = result["id"]
#songs = get_songs_by_artists(token, artist_id)

#for idx, song in enumerate(songs):
#    print(f"{idx + 1}. {song['name']}")

#print(populate_playlist(createplaylist(token, user_id)))


#todo:
#Add image to playlist, news podcasts first, then songs inbetween (some new, some recommended, some taste breakers); 
# daily modify playlist (auto?) - use if statement> once created, will simply modify curren standing one (based off name)
#figure out how to copy url from last page in safari through the python web enviornment

#so my function can do two things
#it can take the current daily drive, and replace it with my news (maybe a special random one in the futuree)
#or it can create a brand new one, based off a playlist of my choosing.