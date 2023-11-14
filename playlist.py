import json
from urllib.parse import urlencode
import base64
import requests
import authtoken
import search
from flask import session
from db import mongo
#HOW TO IMPORT EVERYTHING IN MODULE?

token =""#authtoken.get_accesstoken()
#was token = authtoken.get_token()
user_id = session.get('user') #are these calls okay? they are to null objects, but will i get a re
#refreshed token every time? or will i get the uid even if user doesn to auth page? (set it upon login/entering page?) sessionc ookies makes this already work i think
#token=session.get("accesstoken")  #hmm, maybe i will save this for inbetween function calls. if i leave this static, i know it expires after a few minutes. how will i call a refresh? a refresh in main every time i called every time I run the get_token() funxtion? or get_token() every time is need it?
#print('uid2:')
#print(token)



def set_userid():
    global user_id
    user_id = session.get('user')
    if not user_id:
        print("error, no user in session")
        print(user_id)
        return None
    return user_id



#set_uid()
#this should be in authtoken, specified for each user

#FLASK DEVELOPMENT: I NEED TO MAKE SURE ALL OF MY STATIC PERSONAL REFERENCES ARE OUT OF HERE (SEARCH FOR MY UID and playlist names. also make it to where it will get all playlists for you and filter by ones you own)
#THIS MODULE IS FOR PLAYLIST MANIPULATIONS and creations
#*********** Above are Support Function Calls ***************#

def createplaylist(token, user_id):
    url = f"https://api.spotify.com/v1/users/{user_id}/playlists"

    headers = {"Authorization": "Bearer " + token, "Content-Type": "application/json"} #or token
    
    data = json.dumps({"name": "MY Daily Drive"})
    
    result = requests.post(url, headers=headers, data=data)
    
    json_result = json.loads(result.content)
    
    #print(json_result)
    playlist_id = json_result["id"]
    #
    #f= open("playlist_id.txt","w+")
    #f.write(playlist_id) #save id for later
    #f.close() # close file
    
    authtoken.save_playlistid_db(playlist_id)
    
    #give playlist an image
    image_file=open('./static/dd.jpeg','rb') #url for static
    encoded_string = base64.b64encode(image_file.read())
    
    give_playlist_image(token,playlist_id,encoded_string)
        
    print(f'New Playlist ID Created: {playlist_id}')
    return playlist_id

def remove_track_from_playlist(token,playlist_id,uri):
    url = f"https://api.spotify.com/v1/playlists/{playlist_id}/tracks"
    headers = {"Authorization": "Bearer " + token, "Content-Type": "application/json"} #or token
    #we will do get-uri for a track
    data = json.dumps({
        "tracks":[{
            "uri": f'{uri}'
            }]
        })
    
    #data = f'{"tracks": [{"uri": {uri} }]}'
    result = requests.delete(url,headers=headers,data=data)
    json_result = json.loads(result.content)
    return json_result

#config - with open('.txt', 'a') - it will add/write to the file without deleting it. use \n for a new line

def get_saved_playlist_id(): #returns the playlist_id of the last daily drive playlist created
    #f= open("playlist_id.txt","r")
    #playlist_id=f.read()
    playlist_id=authtoken.get_saved_db_playlistid()
    return playlist_id
    
    
def populate_playlist(playlist_id,uri):
    #url = f"https://api.spotify.com/v1/playlists/{playlist_id}/tracks"
    url = f"https://api.spotify.com/v1/playlists/{playlist_id}/tracks?uris={uri}"
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
    return json_result

def add_batch_to_playlist(playlist_id,uri): #to  add to playlist at the end, simply use a singular uri in populate_playlist() method
    print('Adding Track URIs To Playlist ...')
    #url = f"https://api.spotify.com/v1/playlists/{playlist_id}/tracks"
    url = f"https://api.spotify.com/v1/playlists/{playlist_id}/tracks?uris={uri}"
    headers = {"Authorization": "Bearer " + token, "Content-Type": "application/json"} #or token
    #we will do get-uri for a track
    data = json.dumps({
        "uris": [
            uri
            ]
        })
    
    #or
    #data = f'{"uris": ["{uri}"], "position": 0}'
    
    #NOTE: We got rid of the try-catch statment in this is because, before running this program, we should run the 'update_all_podcasts' function to make sure the uri's are fresh
    result = requests.post(url, headers=headers, data=data)
    
    json_result = json.loads(result.content)
    
    #playlist_id = json_result["id"]
    return json_result

def add_single_to_playlist(playlist_id,uri,position): #to  add to playlist at the end, simply use a singular uri in populate_playlist() method
    #url = f"https://api.spotify.com/v1/playlists/{playlist_id}/tracks"
    url = f"https://api.spotify.com/v1/playlists/{playlist_id}/tracks?position={position}&uris={uri}"
    headers = {"Authorization": "Bearer " + token, "Content-Type": "application/json"} #or token
    #we will do get-uri for a track
    data = json.dumps({
        "uris": [
            uri
            ],
        "posiion": position
        })
    
    #or
    #data = f'{"uris": ["{uri}"], "position": 0}'
    
    try: #see if spotify will take our url, if it wont then our uri is bad
        result = requests.post(url, headers=headers, data=data)
        #print('ERROR: Old URI)
    except:  #if spotify won't take our URI, get a new one amd try again (only once)
        podcast_id = get_podcast_data_from_list(uri,1,2) #get podcast id based off of the uri
        update_podcast(token,podcast_id) #update the list with fresh podcast uri based off found id - this will only take one uri
        print('trying again')
        tries = tries+1 #count number of tries
        if (tries>1): #if this exception was already thrown, cancel out the nested loop
            return 'ERROR: Invalid URI, Too Many Retries'
        add_single_to_playlist(playlist_id,uri,position) #run nested loop

    json_result = json.loads(result.content)
    
    #playlist_id = json_result["id"]
    return json_result

def add_podcasts_to_playlist(playlist_id): #this function adds the podcasts in the json file to the specified playlist through the uri
    print('Adding Podcasts To Playlist  . . .')
    pos = 1
    result = mongo.db.playlists.find({"_id" : session.get("user")}, {"podcasts"}) #or playlist id or name ( i can make my own search function)
    for x in result:
        for podcasts in x["podcasts"]:
            uri=podcasts['uri']
            if not (podcasts['name']=="ABC News Update"):
                uri=podcasts['uri']
                print(podcasts['name'])
                print(add_single_to_playlist(playlist_id,uri,pos))
                pos = pos + 5
            else: 
                print(podcasts['name'])
                uri=podcasts['uri']
                print(add_single_to_playlist(playlist_id, uri, 2)) #Adds ABC News Right After Radio Headspace
                pos = 7
            
            #write to file
    
    return 'Podcasts Added Successfully'

def add_podcasts_to_playlistold(playlist_id): #this function adds the podcasts in the json file to the specified playlist through the uri
    print('Adding Podcasts To Playlist  . . .')
    file=open('podcasts.json','r+')
    json_data=json.load(file)
    
    pos = 1
    
    for index, podcasts in enumerate(json_data['podcasts']): #starts with 2nd podcast in list, news, so we get back to back headspace and news
        uri = podcasts['uri'] # or can do json_data['podcasts'][index]['uri]
        
        if not (json_data['podcasts'][index]['name']=="ABC News Update"):
            print(add_single_to_playlist(playlist_id,uri,pos))
            pos = pos + 5
        else: 
            uri = json_data['podcasts'][1]['uri']
            print(add_single_to_playlist(playlist_id, uri, 2)) #Adds ABC News Right After Radio Headspace
            pos = 7
            
    return 'Podcasts Added Successfully'

def add_podcasts_to_playlistold(playlist_id): #this function adds the podcasts in the json file to the specified playlist through the uri
    print('Adding Podcasts To Playlist  . . .')
    file=open('podcasts.json','r+')
    json_data=json.load(file)
    
    pos = 1
    
    for index, podcasts in enumerate(json_data['podcasts']): #starts with 2nd podcast in list, news, so we get back to back headspace and news
        uri = podcasts['uri'] # or can do json_data['podcasts'][index]['uri]
        
        if not (json_data['podcasts'][index]['name']=="ABC News Update"):
            print(add_single_to_playlist(playlist_id,uri,pos))
            pos = pos + 5
        else: 
            uri = json_data['podcasts'][1]['uri']
            print(add_single_to_playlist(playlist_id, uri, 2)) #Adds ABC News Right After Radio Headspace
            pos = 7
            
    return 'Podcasts Added Successfully'

#def - add podcast - adds this podcasts to the json
def add_podcast_to_list(name):
    podcast_data=search.get_all_podcast_info(token,name)#podcast_info=search.get_all_podcast_info(token,name)
    #podcast_name=podcast_info[0]
    #podcast_id=podcast_info[1]
    #podcast_uri=podcast_info[2]
    #
    #data = {
    #        "name": f"{podcast_name}",
    #        "id": f"{podcast_id}",
    #        "uri": f"{podcast_uri}"
    #    }
    
    uid = session.get('user')
    result=mongo.db.playlists.update_one(
        { '_id': uid }, #specify the document
        { '$addToSet': { 'podcasts': podcast_data } } # must be array. addtoset only adds if it doesnt already exist in array! useful for playlist@
    )
    
    if "'updatedExisting': True" in str(result):
        #print("true")
        print(f'podcast: {podcast_data["name"]} added')
        #return True
        return f"podcast: {podcast_data['name']} added"
    
    return f'podcast: {podcast_data["name"]} not added'

def add_podcast_to_list_old(token,name):
    podcast_info=search.get_all_podcast_info(token,name)
    podcast_name=podcast_info[0]
    podcast_id=podcast_info[1]
    podcast_uri=podcast_info[2]
    
    if(check_is_podcast_listed(podcast_name)):
        return 'ERROR: podcast already in json list'
    
    data = {
            "name": f"{podcast_name}",
            "id": f"{podcast_id}",
            "uri": f"{podcast_uri}"
        }
    
    file=open('podcasts.json','r+')
    json_data=json.load(file)
    json_data["podcasts"].append(data)
    file.seek(0)
    json.dump(json_data, file, indent = 4)
    
    return f'podcast: {podcast_name} added'

def check_is_podcast_listed(podcast_name):
    file=open('podcasts.json','r+')
    json_data=json.load(file)
    
    #search if it exists
    for index, podcasts in enumerate(json_data['podcasts']): #cycles through all elements
        if (podcasts['name']==podcast_name):
            return True
    return False #if all elements are cycled through, returns false

    
def remove_podcast_from_list(token,podcast_name): #remove podcast from list
    file=open('podcasts.json','r+')
    json_data=json.load(file)
    
    podcast_info=search.get_all_podcast_info(token,podcast_name)
    name=podcast_info[0]
    
    if not (check_is_podcast_listed(name)):
        return 'ERROR: podcast not in json list'
    
    uid=session.get('user')
    result = mongo.db.playlists.update_one({"_id": uid}, { '$pull': {"podcasts": { "name" : name}} } ) #deletes the entire entry from array where author is pablo,
    print(result)

    return f'removed playlist: {podcast_name}'

def remove_all_podcasts_from_playlist(playlist_id): #this uses a loop because we have to iterate throguh the uri's one by one
    file=open('podcasts.json','r+')
    json_data=json.load(file)
    
    for index, podcasts in enumerate(json_data['podcasts']):
        uri = json_data['podcasts'][index]['uri']
        result=remove_track_from_playlist(token,playlist_id,uri) #deletes them from playlist
        print(f'Podcasts Successfully Removed {uri} From Playlist {playlist_id}')
    return result

def update_podcast(token, podcast_id):
    file=open('podcasts.json','r+')
    json_data=json.load(file)
    
    #search if it exists
    for index, podcasts in enumerate(json_data['podcasts']): #cycles through all elements
        if (podcasts['id']==podcast_id):
            uri = search.get_mostrecent_podcast_uri(token,podcast_id)
            json_data['podcasts'][index]['uri']=f'{uri}' #update uri;
            file=open('podcasts.json','w')
            json.dump(json_data,file,indent=4) #write into file
            return 'successful'

    return 'unsuccessful'

def update_all_podcasts(token):
    print('Updating All Podcasts ...')
    #result = mongo.db.playlists.find({"_id": uid}, {'podcasts':"Mike"}) #or playlist id or name ( i can make my own search function)
    #for x in result:
    #print(x)
    #search if it exists
    result = mongo.db.playlists.find({"_id" : session.get("user")}, {"podcasts"}) #or playlist id or name ( i can make my own search function)
    try:
        for x in result:
            for podcasts in x["podcasts"]:
                podcast_id=podcasts['id']
                uri = search.get_mostrecent_podcast_uri(token,podcast_id)
                
                query = {"_id": session.get("user"), 'podcasts.id' : podcast_id}
                update = { "$set": {f"podcasts.$.uri" : uri}}
                
                result2=mongo.db.playlists.update_one(query, update)
                
                #print(f"{podcast_id},  uri: {uri}")
                #print(result2)
                
                #the below check returns and error
                #if not "'updatedExisting': True" in result2:
                #    print(f"ERROR UPDATING {podcasts['name']}") #if update was unsucessful, show podcast name and break loop? or pass?
                #    #break
                
                #write to file
        #search if it exists
    except:
        print("ERROR Updating Podcasts: (Maybe They're Currently Uploading!")
        return 'ERROR UPDATING PODCASTS'

    return 'All Podcasts Updated'

def update_all_podcastsold(token):
    file=open('podcasts.json','r+')
    json_data=json.load(file)
    
    print('Updating All Podcasts ...')
    #search if it exists
    try:
        for index, podcasts in enumerate(json_data['podcasts']): #cycles through all elements
            podcast_id=json_data['podcasts'][index]['id']
            uri = search.get_mostrecent_podcast_uri(token,podcast_id)
            json_data['podcasts'][index]['uri']=f'{uri}' #update uri;
            file=open('podcasts.json','w')
            json.dump(json_data,file,indent=4) #write into file
    except:
        print("ERROR Updating Podcasts: (Maybe They're Currently Uploading!")
        return 'ERROR UPDATING PODCASTS'

    return 'All Podcasts Updated'

def get_podcast_data_from_list(podcast_info, output_integer, input_integer): #it will search the list with the information you got and return the information you need via integer. I/O integers are: (0 = name, 1 = id, 2 = uri) - if you are sending a uri, you'll eed the input integer to be 2
    choice = ''
    
    match input_integer: #what type of data is 'podcast_info'?
        case 0:
            choice = 'name'
        case 1:
            choice = 'id' 
        case 2:
            choice = 'uri'
        case _:
            return 'ERROR: Invalid Integer Choice'
    
    file=open('podcasts.json','r+')
    json_data=json.load(file)
    
    idx = ''
    exists = ''
    
    for index, podcasts in enumerate(json_data['podcasts']): #searches podcasts.json via type of data listed above and podcast_info passed
        if (podcasts[choice]==podcast_info): #if podcast info was found, let us know it 'exists' and save it's index
            idx = index
            exists = True
    
    if not (exists==True): #if it did not exist, then return error
        return 'ERROR: podcast is NOT in json list'
    
    podcast_name = json_data['podcasts'][idx]['name'] #get podcast name from index listed
    podcast_info=search.get_all_podcast_info(token,podcast_name) #get all pocast info based off of official name
    
    choice = ''
    
    match output_integer: #what type of data did you want to return?
        case 0:
            choice = 'name'
        case 1:
            choice = 'id' 
        case 2:
            choice = 'uri'
        case _:
            return 'ERROR: Invalid Integer Choice'
    
    return json_data['podcasts'][idx][choice] #returns data type info

def get_podcast_from_list(podcast_name, integer): #DEPRECATED: it will search the list and return the information you need via integer (0 = name, 1 = id, 2 = uri)
    podcast_info=search.get_all_podcast_info(token,podcast_name)
    name=podcast_info[0]
    
    file=open('podcasts.json','r+')
    json_data=json.load(file)
    
    if not (check_is_podcast_listed(name)):
        return 'ERROR: podcast is NOT in json list'
    
    idx = ''
    
    for index, podcasts in enumerate(json_data['podcasts']): #cycles through all elements
        if (podcasts['name']==name):
            idx = index
    
    choice = ''
    
    match integer:
        case 0:
            choice = 'name'
        case 1:
            choice = 'id' 
        case 2:
            choice = 'uri'
        case _:
            return 'ERROR: Invalid Integer Choice'
    
    #print(choice)
    
    return json_data['podcasts'][idx][choice]

def swap_podcast_element_positions(podcast_name,target_index): #swaps podcast_name from it's position with the podcast at target_index
    
    podcast_info=search.get_all_podcast_info(token,podcast_name)
    name=podcast_info[0]
    
    file=open('podcasts.json','r+')
    jsondata=json.load(file)
    
    if not (check_is_podcast_listed(name)):
        return 'ERROR: podcast is NOT in json list'

    idx = ''
    #we will need to find the index of what podcast we want to swap
    for index, podcasts in enumerate(jsondata['podcasts']):
        if (podcasts['name']==podcast_name):
            #print(index,podcasts)
            idx = index

    #all we need are the two indices we want to swap. one will be saved to be replaced, and the other will simply be overwritten
    temp = jsondata['podcasts'][idx]  #save pre-existing element to a temp directory
    jsondata['podcasts'][idx]=jsondata['podcasts'][target_index] #place target element into the target index
    jsondata['podcasts'][target_index]=temp #place the pre-existing element into the target element's previous index

    file=open('podcasts.json','w')#write changes
    json.dump(jsondata, file, indent = 4)
    return f"sucessfully swapped {jsondata['podcasts'][idx]['name']} positions with {jsondata['podcasts'][target_index]['name']}"

def compile_uris_from_list(): #takes in a json file of a list from the get_playlist_tracks
    uris = ''
    file=open('podcasts.json','r+')
    json_data=json.load(file)
    
    #update all podcast uris
    #update_all_podcasts(token) we don't want to do this becuase we will need the old uri's to delete from the podcast
    
    #search all podcasts in lists - iterates and updates each podcast upon compile
    for index, podcasts in enumerate(json_data['podcasts']): #cycles through all elements
        uri=json_data['podcasts'][index]['uri']

        uris = uris+f'{uri},'
        
        file=open('podcasts.json','w')
        json.dump(json_data,file,indent=4) #write into file

    return uris


def give_playlist_image(token, playlist_id, encoded_string):
    url = f"https://api.spotify.com/v1/playlists/{playlist_id}/images"
    headers = {"Authorization": "Bearer " + token, "Content-Type": "image/jpeg"} 
    data = encoded_string
    result = requests.put(url, headers=headers, data=data)
    #json_result = json.loads(result.content)
    print('Playlist Image Updated')
    return result

def duplicate_original_daily_drive_tracks(token,playlist_id): #took away playlist_id field, althought it should've remained for duplicating to pre-existing playlist
    uris = search.get_daily_drive_tracks_uris(token) # i can make a simple function for this - get daily drive track_uris
    populate_playlist(playlist_id,uris) 
    #NOT DONE - need to write code to copy the podcasts over, save their uris, and also code to replace the current podcast with updated podcast episode
    #the above still needs to be done, however, currently this only copys songs in daily drive, so we are ok for now.
    print('Original Daily Drive Tracks Duplicated')

def add_dd_opening_track():#I can also save the uri's of the opening track and build them as needed
    print('Adding Opening Track...')
    p_id='37i9dQZF1EfFTETp5u0zCK' #static, the daily drive id shouldn't change... if it does, I can use the search podcast feature to keep this id up to date
    opening_uri=search.get_spotify_dd_opening(token,p_id)
    result=add_single_to_playlist(get_saved_playlist_id(),opening_uri,0) #adds the uri to the begining of the playlist. Ideally, this should be done after populating the playlist with tracks
    return result

def delete_old_custom_dd_playlist(): #according to spotify, for all intents and purposes this is really essentially unfollowing a playlist
    print('Deleting Old Daily Drive Playlist In Database')
    p_id=authtoken.get_saved_db_playlistid()
    #p_id=get_saved_playlist_id()
    url = f"https://api.spotify.com/v1/playlists/{p_id}/followers"
    headers = {"Authorization": "Bearer " + authtoken.get_token(), "Content-Type": "application/json"} #or token

    result = requests.delete(url,headers=headers)
    #try:
    #    result = requests.delete(url,headers=headers)
    #except:
    #    json_result = json.loads(result.content)
    #    #or: print(f'There is no playlist with id: ',p_id) [but the above should send said message?
    #else:
    #    json_result = json.loads(result.content)
    return result

def unfollow_playlist(playlist_id): #according to spotify, for all intents and purposes this is really essentially unfollowing a playlist
    url = f"https://api.spotify.com/v1/playlists/{playlist_id}/followers"
    headers = {"Authorization": "Bearer " + token}#, "Content-Type": "application/json"} #or token

    try:
        result = requests.delete(url,headers=headers)
    except:
        json_result = json.loads(result.content)
        #or: print(f'There is no playlist with id: ',p_id) [but the above should send said message?
    else:
        json_result = json.loads(result.content)

    return json_result
    
#*********** Above are Support Function Calls ***************#
#*********** Below are Main Function Calls ***************#

#SO - > The master function, the one doing all the calls, essentially running the file, will have to be the one to initilize user_id equal to session uid. This cannot happen upon import because the user may not be logged in yet at that time. Same thing with token
def build_daily_drive_playlist(integer,playlist_selection_id): #Creates the daily drive playlist and auto-populates it with playlist and podcast tracks/function calls depending on the options
    #for debug
    #global user_id
    #print("user id:")
    #print(authtoken.get_sessionid())
    #print(session.get('user'))
    #print(user_id)
    
    #print("try 2") #it works!!!!
    #set_userid() #sets automatically to session value
    #print(user_id)
    
    #FIRST: make sure when search.py is called that it inherits this user_id somehow?...
    #now lets get token working:
    
    #something=authtoken.get_accesstoken()
    
    #print("SO THE CODE I END UP WITH IS[THIS TXT IS MARKER ONLY]")
    
    #print(something)
    
    
    #token=session.get("accesstoken") #get the access token from session
    #maybe i can run set token for all models here
    #this works!
    #print(token)
    #set_token(token)
    #print()
    #i also have to do this in search, if search requires access to any of this information
    
    
    #what if i created a function that ran every time i want to call
    #something from playlist.py, that set all the variables
    #so i don thave to worry about doing it every call?
    match integer: #0 - original with my podcasts, 1 - new with my playlist and podcasts, 2 - same as 1 but shuffled tracks
        case 0: #this duplicates the originaly daily drive tracks and places in my own podcasts in them
            print('Starting: Duplicating Original Daily Drive Playlist')
            delete_old_custom_dd_playlist()
            print(update_all_podcasts(token))
            playlist_id=createplaylist(token,user_id)
            duplicate_original_daily_drive_tracks(token,playlist_id) #change this for each user
            add_podcasts_to_playlist(playlist_id)
            print('Finished Building Daily Drive Duplicate')
        case 1: # builds a new daily drive with my podcasts and playlist of choice but does not shuffle songs (useful for spotify featured playlists that constantly update)
            print('Starting: Building New Daily Drive With Custom Playlist[No Shuffle]')
            delete_old_custom_dd_playlist()
            print(update_all_podcasts(token))
            playlist_id=createplaylist(token,user_id)
            uris=search.compile_track_uris(search.get_playlist_tracks(token,playlist_selection_id))
            print(add_batch_to_playlist(playlist_id,uris))
            add_dd_opening_track()
            add_podcasts_to_playlist(playlist_id)
            print('Finished Building New Daily Drive With Custom Playlist[No Shuffle]')
        case 2: # builds a new daily drive with my podcasts and playlist of choice, shuffles the songs for me
            print('Starting: Building New Daily Drive With Custom Playlist[Shuffle]')
            delete_old_custom_dd_playlist()
            print(update_all_podcasts(token))
            playlist_id=createplaylist(token,user_id)
            uris=search.shuffle_compile_playlists_tracks(playlist_selection_id)
            print(add_batch_to_playlist(playlist_id,uris))
            add_dd_opening_track()
            add_podcasts_to_playlist(playlist_id)
            print('Finished Building New Daily Drive With Custom Playlist[Shuffle]')
    return 'Daily Drive Built'

def refresh_daily_drive_podcasts(): #this replaces the podcasts in the latest dd created with new updated podcasts! incase i wanna keep the shuffle/songs i have
    print(remove_all_podcasts_from_playlist(get_saved_playlist_id()))
    print(update_all_podcasts(token))
    print(add_podcasts_to_playlist(get_saved_playlist_id()))
    return 'Podcasts Refreshed In Playlist' # instead of making a refresh function that reshuffles the entire playlist or it's song's, I can just run the shuffle build function again



def get_user_playlists(limit,offset): #how to get only my playlists, -> NOTE: {offset} simply offsets the playlist numbers listed, NOT the page (so offset=5 means it will omit the first 5 playlist, not page of playlists. offset should =limit%2=0)
    url = f"https://api.spotify.com/v1/users/{user_id}/playlists?limit={limit}&offset={offset}"
    headers = {"Authorization": "Bearer " + token}#, "Content-Type": "image/jpeg"} 
    result = requests.get(url, headers=headers)
    json_result = json.loads(result.content)
    #print('Playlist Image Updated')
    
    for index, items in enumerate(json_result['items']):
        name = json_result['items'][index]['name']
        id = json_result['items'][index]['id']
        owner = json_result['items'][index]['owner']['display_name']
        print(f'{index}. {name}, {id}, {owner}')
        
    return json_result

def get_user_owned_playlists(limit,offset): #how to get only my playlists,
    url = f"https://api.spotify.com/v1/users/{user_id}/playlists?limit={limit}&offset={offset}"
    headers = {"Authorization": "Bearer " + token}#, "Content-Type": "image/jpeg"} 
    result = requests.get(url, headers=headers)
    json_result = json.loads(result.content)
    #print('Playlist Image Updated')
    
    for index, items in enumerate(json_result['items']):
        if(json_result['items'][index]['owner']['display_name']==authtoken.get_user_db_info.username):
            name = json_result['items'][index]['name']
            id = json_result['items'][index]['id']
            owner = json_result['items'][index]['owner']['display_name']
            print(f'{index}. {name}, {id}, {owner}')
            
    print(json_result['total']) #get total of playlists I have
    print(json_result['offset'])
        
    return json_result

def check_is_playlist_listed2(playlist_id): #this si for getting all my owned playlsit function
    file=open('PlaylistsSave.json','r+')
    json_data=json.load(file)
    
    #search if it exists
    for index, playlists in enumerate(json_data['playlists']): #cycles through all elements
        if (playlists['id']==playlist_id):
            file.close()
            return True
        
    file.close()
    return False #if all elements are cycled through, returns false

def get_all_user_owned_playlists(): #how to get all only my playlists
    offset = 0 #int to 1100 for test, start at 0 for actual
    uid=session.get('user')
    url = f"https://api.spotify.com/v1/users/{uid}/playlists?limit=50&offset={offset}" #limit is set to 50 because thats the max, i can also omit it altogether
    headers = {"Authorization": "Bearer " + authtoken.get_token()}#, "Content-Type": "image/jpeg"} 
    result = requests.get(url, headers=headers)
    print(result)
    json_result = json.loads(result.content)
    
    total_playlists = json_result['total'] #get total of playlists I have
    #offset = json_result['offset'] #current offset of playlists, this ups automatically until the end
    playlist_count = 0 #count how many playlists are mine
    
    while offset < total_playlists: #when offset reaches max number of playlist stops
 
        url = f"https://api.spotify.com/v1/users/{uid}/playlists?limit=50&offset={offset}"
        result = requests.get(url, headers=headers)
        json_result = json.loads(result.content)
        
        for index, items in enumerate(json_result['items']): #iterate through this page of playlists
            if(json_result['items'][index]['owner']['display_name']==authtoken.get_current_user_db_info().username): #if the playlists are mine... add them to the json (or in this case, the list of available playlists to choose from)  NOTE: for spotify featured playlists and not my own, I can simply do playlists that aren't mine w/ !, or get rid of if altogether for all resuls (there's 1290 though)
                id = json_result['items'][index]['id']
                result=add_playlist_to_list(id)
                #print(authtoken.get_current_user_db_info().username)
                playlist_count=playlist_count+1
                if result == False:
                    print('error getting user owned playlists')
                    break
    
        #print(offset) prints progress; when offset is >total playlists the loop closes
        #print(total_playlists)
        #print()
        offset = offset + 50 #next group of playlists
              
    #return json_result
    return playlist_count


def search_my_playlistsSave_lists(search_item): #where ITEM is what we are searching, TYPE is what attribute it is, and RETURN is what we want to get from our search i.e. a playlist id. For checking if an element exists, see check_playlist_list or something like that - can use this for same function too though, using the error message as a 'does not exist' type of response but if we simply type in a name werong then we're sol
    file=open('playlistsSave.json','r+')
    json_data=json.load(file)
    
    print(json_data)
    for index, playlists in enumerate(json_data['playlists']):
        if search_item in playlists['name']: #if our search is successful, it will return what we searched back
            #print(playlists['name'], playlists['id'], playlists['url'], playlists['owner']) #maybe save to list?
            print(f'{index}. {playlists["name"]} {playlists["owner"]} {playlists["id"]}')
    
    return 'done'
   
#*********** Above are Main Function Calls ***************#

#playlistid='7HedC7XXPoF6I1NyJVPaNx'
#print(build_daily_drive_playlist(2,playlistid)) #ADD PRINT STATEMENT FOR WHAT SONGS/PLAYLIST IS BEING ADDED

#*********** Notes: ***************#

def get_my_playlists(): #returns a list of my playlists (playlists with attribute: owned by me); prob need to run in search - try search with artist playlist having my name OR running a get users playlist loop that filters playlist with attributed owner: 'me', and increases the offset by 99 each time until it reaches the end (will have to figure out how to end loop) - save to json/print out list? (probably save to json)
    return ''


def get_my_playlist_id_from_json(playlist_name, playlist_index): #gets my playlist name from choicesi choose via index , or can search it (split into two functions?)
    return ''

def display_my_playlist_list(): #Displays id, name, and index
    file=open('myplaylists.json','r+')
    json_data=json.load(file)
    
    for index, playlists in enumerate(json_data['playlists']):
        print(f"Name: {playlists['name']}")
        print(f"ID: {playlists['id']}")
        print(f"Owner: {playlists['owner']}")
        print(f"URL: {playlists['url']}")
        print(f'Index: {index}') #can set these to variables and return them - can make fucntion 'parse my playlist info' - or playlists_list_info
        print() 
    
    return 'Playlist List Printed'

import re

#uses the 're' import
#print(search_my_playlists_lists('So Much Soul','name','name'))
def search_my_playlists_lists(search_item,search_type,return_type): #where ITEM is what we are searching, TYPE is what attribute it is, and RETURN is what we want to get from our search i.e. a playlist id. For checking if an element exists, see check_playlist_list or something like that - can use this for same function too though, using the error message as a 'does not exist' type of response but if we simply type in a name werong then we're sol
    file=open('myplaylists.json','r+')
    json_data=json.load(file)
    index = 0
    #return_type=''
    
    for index, playlists in enumerate(json_data['playlists']):
        try: #catch faulty search type
            result = re.search(f'{search_item}', f'{playlists[f"{search_type}"]}') #searches for the type of data we want to match with our search
        except:
            return 'ERROR: Invalid Search Only types allowed are: "name","id","owner", and"url"' 
        
        #should add a try statment here to catch no results found i.e. faulty search item
        if(result.group(0)==search_item): #if our search is successful, it will return what we searched back
            try: #catch faulty return type
                print('index: ',index)
                print(playlists['name'])
                return playlists[f'{return_type}']
            except:
                return 'ERROR: Invalid Return Only types allowed are: "name","id","owner", and"url"'
    
    return 'something went wrong in search (i think)' #it shouldn't reach this statement at all, right? it should be an error, or a search not found message

#my own python search filter, for myplaylist list - if not there, i would prompt - want to searcxh all of spotify w warning: could get random playlist (or put in owner)

def check_is_playlist_listed(playlist_id): #this method is not needed but it is replaced now with this
    uid = session.get('user')
    if(mongo.db.playlists.find_one({ "_id" : uid }, { "playlists" : {'id': playlist_id} })):
        return True
    return False #if all elements are cycled through, returns false

def check_is_playlist_listed(playlist_id):
    file=open('myplaylists.json','r+')
    json_data=json.load(file)
    
    #search if it exists
    for index, playlists in enumerate(json_data['playlists']): #cycles through all elements
        if (playlists['id']==playlist_id):
            return True
    return False #if all elements are cycled through, returns false

def add_playlist_to_list(playlist_id,genre="Undefined"):
    playlist=search.get_playlist_info(playlist_id) #make this a search function that matched id to name?
    playlist_name=playlist['name']
    playlist_owner=playlist['owner']['display_name']
    playlist_id=playlist['id']
    playlist_url=playlist['external_urls']['spotify']
    
    data = {
            "name": f"{playlist_name}",
            "owner": f"{playlist_owner}",
            "id": f"{playlist_id}",
            "url": f"{playlist_url}",
            "genre": f"{genre}" #may take this out, as its a variable i put in
        }
    
    uid = session.get('user')
    result=mongo.db.playlists.update_one(
        { '_id': uid }, #specify the document
        { '$addToSet': { 'playlists': data } } # must be array. addtoset only adds if it doesnt already exist in array! useful for playlist@
    )
    
    if "'updatedExisting': True" in str(result):
        #print("true")
        return f'playlists: {playlist_name} added'
        #return True
    
    #if its already in the array it will skip it automatically!
    print(f'could not add playlist: {playlist_name} [NOT ADDED]')
    return None

def add_playlist_to_list_old(playlist_id,genre): #add a search function that matches the name i put into the id i need (if i need it)
    playlist=search.get_playlist_info(playlist_id) #make this a search function that matched id to name?
    playlist_name=playlist['name']
    playlist_owner=playlist['owner']['display_name']
    playlist_id=playlist['id']
    playlist_url=playlist['external_urls']['spotify']
    
    uid = session.get('user')
    if(mongo.db.playlists.find_one({ "_id" : uid }, { "playlists" : {'id': playlist_id} })):
        return 'ERROR: playlist already in json list'
    
    data = {
            "name": f"{playlist_name}",
            "owner": f"{playlist_owner}",
            "id": f"{playlist_id}",
            "url": f"{playlist_url}",
            "genre": f"{genre}" #may take this out, as its a variable i put in
        }
    
    #file=open('myplaylists.json','r+')
    #json_data=json.load(file)
    #json_data["playlists"].append(data)
    #file.seek(0)
    #json.dump(json_data, file, indent = 4)
    
    #uid=session.get('user')
    #mongo.db.playlist
    
    result=mongo.db.playlists.update_one(
        { '_id': uid }, #specify the document
        { '$push': { 'playlists': data } } # must be array. addtoset only adds if it doesnt already exist in array! useful for playlist@
    )

    if "'updatedExisting': True" in str(result):
        print("true")
        return f'playlist: {playlist_name} added'
    return f'could not add {playlist_name}'



def remove_playlist_from_list(playlist_id): #remove podcast from list
    file=open('myplaylists.json','r+')
    json_data=json.load(file)
    
    #podcast_info=search.get_all_podcast_info(token,podcast_name) #SEARCH FUCNTION - should i implement another function for this? filter out owners to me
    #name=podcast_info[0]
    
    if not (check_is_playlist_listed(playlist_id)):
        return 'ERROR: podcast not in json list'
    
    for index, playlists in enumerate(json_data['playlists']):
        if (playlists['id']==playlist_id):
            playlist_name=playlists['name']
            json_data['playlists'].pop(index)
    
    file=open('myplaylists.json','w')
    json.dump(json_data,file,indent=4) #write into file

    return f'removed playlist: {playlist_name}'

def set_token(t):
    global token
    token=t
    if "error" in token:
        print("token has an error")
        print(token)
        return None
    return token

def setglobalvariables():
    set_userid()
    set_token(session.get('accesstoken'))
    return None
# NEXT TO DO:

#make it a web app first - how to make python a compiled app /w gui?
#look in master notes for final steps

# RANDOMIZED PODCASTS: eventually, randomly select a podcast from a given genre during the week - daily drive does this daily, so i can copy theirs if i want. but sometimes theirs is boring. but i can copy and compare their playlist and move from there; or search by genre, or completely randomly (or randomly alternate from pre-listed genres or podcast names)

# FIND MY PLAYLISTS: write a function that gets one of my saved playlist ids from a list given a name i search OR gets me options of my main playlists from a list i make - tip: maybe get playlists only owned by me?
# then, get a function that randomly selects a playlist i own or follow (can toggle this)
# when shuffling playlist, also randomze the offset number


# CLEANING: streamline it clean, set up main.py, put it together there, put all functions to their perspective file, [SAVE CODE COMMENTS]I need to figue out how to import all files in this package as a module; clean file list; SAVE CODING COMMENTS

# AUTH CODE: figure out how to copy url from last page in safari through the python web enviornment

# REFRESHING: maybe a catch or listener; everytime a podcast is uploaded from a publisher in my list, it updates it in th
#  e podcast automatically. (how does spotify automate this?) - OR i can just run the refresh podcast playlist every hour - how to have this run even when code is not? (api?)


# AFTER THE ABOVE IS DONE:
# figure out how to add this python code to iphone swift app, or onto an online html app (maybe i can run it on a website)
#NOTE: MAY NOT NEED THE BELOW FUNCTIONS IF I CAN JUST GET ALL OF MY PLAYLISTS AND SEARCH THROUGH THE JSON FILE WITH THEM!!! OR SUBSCRIBED PLAYLIST
#HOWEVER: IT MAY BE BENEIFICIAL TO HAVE A LSIT OF RECENTLY/MOST USED/FAVORITE PLAYLISTS to skip through having to search through my playlists every time (maybe a reuse/rebuild last daily drive button)



#NEEXT NEXT TODO gui:
# a config function to omit headspace/podcasts in the build (simple checkbox for podcasts, the more podcasts the more it makes it. should cap it at 5/6)
#dont forget tha random fun podcast w/ config options
# a simple refresh button to simple shuffle the tracks (not delete playlsit if i want to use this one?)




