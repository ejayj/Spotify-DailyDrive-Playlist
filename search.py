import json
from urllib.parse import urlencode
import requests
import authtoken
import random
from flask import session
#token = authtoken.token #may need to get rid of this
user_id = session.get('user') #this should be in authtoken, specified for each user
token = session.get('accesstoken')

#this module is for searching for URIs, IDs, and tracks
#***********  Below are Support Function Calls ***************#
def get_podcast_id(token, podcast_name):
    #token=authtoken.get_token()
    url = "https://api.spotify.com/v1/search"
    headers = authtoken.get_auth_header(authtoken.get_token())
    query = f"?q={podcast_name}&type=show&limit=1"
    query_url = url + query 
    result = requests.get(query_url, headers=headers)
    json_result = json.loads(result.content)
    #print(json_result)
    if len(json_result) == 0:
        print("not artist with this name exists")
        return None
    json_result = json_result["shows"]["items"]
    id = json_result[0]["id"]
    name = json_result[0]["name"]
    return name,id
    #return json_result
    
def get_podcast(podcast_name):
    #token=authtoken.get_token()
    url = "https://api.spotify.com/v1/search"
    headers = authtoken.get_auth_header(authtoken.get_token())
    query = f"?q={podcast_name}&type=show&limit=1"
    query_url = url + query 
    result = requests.get(query_url, headers=headers)
    json_result = json.loads(result.content)
    print(json_result)
    if len(json_result) == 0:
        print("not artist with this name exists")
        return None
    json_result = json_result["shows"]["items"]
    id = json_result[0]["id"]
    name=json_result[0]['name']
    return name
    #return json_result

def get_mostrecent_podcast_uri(token, id):
    #token=authtoken.get_accesstoken()
    #print("SEARCH TOKEN:")
    
    #print(session.get('accesstoken'))
    #print(token)
    #set_token(token) #set saved token for entire file!
    url = f"https://api.spotify.com/v1/shows/{id}/episodes?limit=1"
    headers = authtoken.get_auth_header(authtoken.get_token())
    result = requests.get(url,headers=headers)
    json_result = json.loads(result.content)
    #print(json_result)
    #print(json_result)
    json_result = json_result["items"]
    uri = json_result[0]["uri"] #most recent podcast is at the top
    name = json_result[0]['name']
    #print("this is the name")
    #print(name)
    return uri

def get_dd_id(token):
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
    id = json_result[0]["id"]
    return id


def get_spotify_dd_opening(token, playlist_id):
    url = f"https://api.spotify.com/v1/playlists/{playlist_id}/tracks?offset=0&limit1"
    headers = authtoken.get_auth_header(token)
    result = requests.get(url, headers=headers)
    json_result = json.loads(result.content)
    json_result = json_result["items"]
    uri = json_result[0]["track"]["uri"]
    return uri

def get_playlist_tracks_limit(token, playlist_id,limit):
    url = f"https://api.spotify.com/v1/playlists/{playlist_id}/tracks?fields=items(track(name,type,uri))&limit={limit}"
    headers = authtoken.get_auth_header(token)
    result = requests.get(url, headers=headers)
    json_result = json.loads(result.content)
    json_result = json_result["items"]
    uri = json_result#[0]["track"]#["uri"]
    return uri

def get_playlist_tracks(token, playlist_id):
    print('Retrieving Playlist Tracks ...')
    url = f"https://api.spotify.com/v1/playlists/{playlist_id}/tracks?fields=items(track(name,type,uri))"# retruns name, type and uri #?offset=0&limit=" #unfinished, needs max - completed in next line
    headers = authtoken.get_auth_header(token)
    result = requests.get(url, headers=headers)
    json_result = json.loads(result.content)
    #print(json_result)
    json_result = json_result['items']
    uri = json_result#[0]["track"]#["uri"]
    return uri

def get_playlist_tracks_shuffle(token, playlist_id): #to be integrated with with the compile_uris_shuffling for large number of tracks
    print('Retrieving Playlist Tracks ...')
    
    url = f"https://api.spotify.com/v1/playlists/{playlist_id}/tracks"#?fields=items(track(name,type,uri))"# retruns name, type and uri #?offset=0&limit=" #unfinished, needs max - completed in next line
    headers = authtoken.get_auth_header(authtoken.get_token())
    offset = 0 #offset=350 for a test

    result = requests.get(url, headers=headers)
    json_result = json.loads(result.content)
    total_playlist_items = json_result['total']
    uris=''
        
    while offset < total_playlist_items: #when offset reaches max number of playlist stops
        url2=f"https://api.spotify.com/v1/playlists/{playlist_id}/tracks?offset={offset}"
        result = requests.get(url2, headers=headers)
        json_result = json.loads(result.content)
        
        for index, items in enumerate(json_result['items']): #iterate through this page of playlists
            newindex=index+offset #numbers it all to 438
            try:
                #print(f'{newindex}. {json_result["items"][index]["track"]["name"]} {json_result["items"][index]["track"]["uri"]}') #see what tracks work
                uris=uris+f'{json_result["items"][index]["track"]["uri"]},'
            except:
                pass
        
        offset=offset+50
            
    
    #print(json_result["items"][3]["track"]["name"])
    #file=open('newnewnew.json','w+')
    #json_data=json.load(file)
    #file.seek(0)
    #json.dump(json_result, file, indent = 4)
    
    #print(json_result)
    #json_result = json_result['items']
    #uri = json_result#[0]["track"]#["uri"]
    
    
    result_list = uris.split(',') #splits raw uris into an organized list, uris alone is mess of a single text dock
    result_list.pop(len(result_list)-1) #get rid of end list null element
    #print(result_list)
    return result_list

def shuffle_compile_uris_2(uris_list): #takes in a json file of a list from the get_playlist_tracks_shuffle; included in the funcgtion
    print('Shuffling URIs')
    uris = ''
    maxrange = len(uris_list)
    #fix the max range integer to be within range
    maxrange = maxrange - 1
    
    #generate 28 songs out of the avaialble max range of indecies; this method makes a list of indecies that do not repeat
    random_track_indices = random.sample(range(maxrange),28)
    
    for x, index  in enumerate(random_track_indices):
        
        #uris = uris + f"{json_result[random_track_indices[x]]['track']['uri']},"
        
        #print(uris_list[random_track_indices[x]])
        uris = uris + f'{uris_list[random_track_indices[x]]},' #get random song
    #print(maxrange) to test max range (should be 1- however many tracks there are because the track indecies start at 0)
    return uris

def shuffle_compile_playlists_tracks(playlist_selection_id): #this is the main function that joins the two shuffling playlist functiosn together (for bigger playlists), see the snapshot save for the original copy of th functions (Still saved)
    uris=shuffle_compile_uris_2(get_playlist_tracks_shuffle(token,playlist_selection_id))
    return uris

def compile_uris(json_result): #takes in a json file of a list from the get_playlist_tracks
    uris = ''
    
    print('Compiling URIs')
    for index, uri in enumerate(json_result['items']): #cycles through all elements
        uri=json_result['items'][index]['track']['uri']#[index]['name']#['items'][index]#['uri']
        uris = uris+f'{uri},'
        #print(uris)

    return uris

def get_daily_drive_tracks_uris(token):
    uris=compile_track_uris(get_dailydrive_tracks(token))
    return uris


def get_all_podcast_info(token, name): #we want id, uri, and name
    set_token(token)
    podcast_name, podcast_id=get_podcast_id(token,name) #searches id via name
    podcast_uri=get_mostrecent_podcast_uri(token,podcast_id) #searches latest episode via uri

    #the below is really extra!
    #podcast_name=get_podcast_show_title(token,podcast_id) #returns actual name via id used to get the episode uri
    #podcast_episode_id=get_mostrecent_podcast_by_id(token,podcast_id)
    data = {
            "name": f"{podcast_name}",
            "id": f"{podcast_id}",
            "uri": f"{podcast_uri}"
        }
    #podcast_info = [podcast_name,podcast_id,podcast_uri] #this is our python list of all podcast info we need for json files
    return data#podcast_info

def get_podcast_episode_name_from_podcastid(token, id):
    url = f"https://api.spotify.com/v1/shows/{id}/episodes?limit=1"
    headers = authtoken.get_auth_header(token)
    result = requests.get(url,headers=headers)
    json_result = json.loads(result.content)
    json_result = json_result["items"]
    name = json_result[0]["name"] #most recent podcast is at the top
    return name

def get_podcast_episode_id_from_podcastid(token, id):
    url = f"https://api.spotify.com/v1/shows/{id}/episodes?limit=1"
    headers = authtoken.get_auth_header(token)
    result = requests.get(url,headers=headers)
    json_result = json.loads(result.content)
    json_result = json_result["items"]
    name = json_result[0]["id"] #most recent podcast is at the top
    return name

def get_mostrecent_podcast_by_id(token, id):
    url = f"https://api.spotify.com/v1/shows/{id}/episodes?limit=1"
    headers = authtoken.get_auth_header(token)
    result = requests.get(url,headers=headers)
    json_result = json.loads(result.content)
    json_result = json_result["items"]
    uri = json_result[0]["id"] #most recent podcast is at the top
    return uri

def get_podcast_show_title_from_episode_id(token, id):
    url = f"https://api.spotify.com/v1/episodes/{id}"
    headers = authtoken.get_auth_header(token)
    result = requests.get(url,headers=headers)
    json_result = json.loads(result.content)
    json_result = json_result["show"]
    name = json_result["name"]#[0]["id"] #most recent podcast is at the top
    return name

#uri=json_result['items'][index]['track']['uri']#[index]['name']#['items'][index]#['uri']
#        uris = uris+f'{uri},'
        #print(uris)
        
def get_playlist_info(playlist_id):  #test with 2FRLYxNARiIsJpajtLtzIp - #it will print the emoji of the playust name, but i cannot reverse search that emoji - even in the spotify app you cant search emojis, no use doing it here
    token=session.get('accesstoken')
    url = f"https://api.spotify.com/v1/playlists/{playlist_id}"
    headers = {"Authorization": "Bearer " + token}#, "Content-Type": "application/json"} #or token
    result = requests.get(url,headers=headers)
    json_result = json.loads(result.content)#['name']
    return json_result

#*********** Above are Support Function Calls ***************#
#*********** Below are Main Function Calls ***************#

def get_latest_podcast(token, podcast_name): #gets the latest podcast of your choice
    podcast_id=get_podcast_id(token, podcast_name)
    uri = get_mostrecent_podcast_uri(token, podcast_id)
    return uri

def get_podcast_show_title(token,podcast_id):
    episode_id=get_podcast_episode_id_from_podcastid(token, podcast_id)
    title = get_podcast_show_title_from_episode_id(token, episode_id)
    return title

def get_playlist_track_rename_me(token, playlist_name, amount): #maybe keep save ids of the playlists; name is string, amounts is amount of tracks
    return get_playlist_tracks

def get_dailydrive_openingtrack_uri(): #returns uri of the custom daily drive opening track
    playlist_id=get_dd_id(token)
    uri=get_spotify_dd_opening(token,playlist_id)
    return uri

def get_dailydrive_tracks(token): #uris of all the tracks in daily drive
    playlist_id=get_dd_id(token)
    uri=get_playlist_tracks(token,playlist_id)
    return uri

def compile_track_uris(tracks): #takes in a json file of a list from the get_playlist_tracks
    print('Compiling Track URIs ...')
    uris = ""

    for idx, track in enumerate(tracks):
        if(tracks[idx]['track']['type']=='track'):
            uris = uris + f"{tracks[idx]['track']['uri']},"
    return uris

def compile__all_uris(uris): #takes in a json file of a list from the get_playlist_tracks
    
    return uris

def shuffle_compile_uris(json_result): #takes in a json file of a list from the get_playlist_tracks
    uris = ''
    maxrange = 0
    
    print('Shuffling URIs')
    for index in enumerate(json_result): #get number of elements - maybe make a random offset?
        maxrange = maxrange + 1
    
    #fix the max range integer to be within range
    maxrange = maxrange - 1
    
    #generate 28 songs out of the avaialble max range of indecies; this method makes a list of indecies that do not repeat
    random_track_indices = random.sample(range(maxrange),28)
    
    for x, index  in enumerate(random_track_indices):
        #uris=json_result[random_track_indices[x]]['track'] #use this to check the track names being accessed
        uris = uris + f"{json_result[random_track_indices[x]]['track']['uri']},"
        #print(uris) #test line
    #print(maxrange) to test max range (should be 1- however many tracks there are because the track indecies start at 0)
    
    return uris

#*********** Above are Main Function Calls ***************#

def set_token(t):
    global token
    token=t
    return token