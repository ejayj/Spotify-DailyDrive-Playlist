from urllib.parse import urlencode
import authtoken #these, and below, are my modules *********
import playlist

token = authtoken.get_token()
user_id = "31dck52ytkqtrzfat2rb6ox5z72y" #this should be in authtoken, specified for each user


playlistid='7HedC7XXPoF6I1NyJVPaNx'
print(playlist.build_daily_drive_playlist(2,playlistid))

#This will be the main python file where we call all the modules together and automate the initial auth code, and playlist creation

#*********** Below are Main Function Calls ***************#
create_daily_drive() #this function creates a new daily drive playylist based on your setting choice (parameter is an int) - (everytime create_daily_drive is ran, a random fun podcast will be placed in there from any given category with a minimum popularity level?)
#calls the corresponding create_playlist function in playlist.py that fits with the integer passed in parameters

# how it will work : ********
# 1. (OPTIONAL) configure daily drive playlist (select podcasts i want, and music playlist i want to mix with) - this essentially just edits text files with what we need
# 2. create daily drive playlist function (calls functiondumps data from text files into code to build playlist) - if one already exists (in a text doc save), then it will delete that one or overwrite it?
# - options: [0] create based off of current daily drive (create_daily_drive(0)) (just replaces podcasts); 
# - options: [1] create based off selected song playlist id in txt doc (create_daily_drive(1)) - if no playlist is in the text file (write function to check this), then it will default to (create_daily_drive(0)) OR put in random reccomended tracks - will also need to write a program to randomly select tracks from said playlist
# 3. (OPTIONAL) modify daily drive playlist - can swap out songs or podcast, or the playlist daily drive is based on

refresh_daily_drive() #this will repopulate the daily drive with updated podcast episodes and new song tracks, essentially re-running the create_daily_drive() function with it's last used paramters - but doesn't delete the playlist, just updates the podcasts currently in there (everytime create_daily_drive is ran, a random fun podcast will be placed in there from any given category with a minimum popularity level?) it should keep this by getting podcast show ids and getting latest updated show - write function for if a uri is not found when added, it will automatically refresh results to produce the most recent uri [and maybe set callback from abc new to 0 upon each fresh run]


config_daily_drive(choice,types) #this will take in parameters of what you want to do where choice is add or remove and type is podcast/playlist or song
#changes the playlist we can use for the songs - the playlist_id can be saved to a text file
#opens a config menu of different things you can config abt the daily drive playlist. should the below be in there?
#can also edit podcast selection

modify_daily_drive() #if changes were made to config daily drive after create was ran, we can use this function to simply update the playlist with the new configurations. (like refresh_daily_Drive since it runs off of the given text files which are updated by config)
#this can also swap out singular podcast shows for different ones if wanted, or repopulate the daily drive with a whole new song playlist selection or basic changes to all playlist parameters like make it private, or delete the playlist altogether,



#the below essentially belongs in config.pu
#--- it will use a switch statement -------
config_daily_drive_podcast() #takes in podcast name and add/remove a podcast from the daily drive (it changes the txt file)  - if podcast not found returns podcast not found

config_daily_drive_playlist() # 
#the below can be in the config .py
#this will take in add/delete, uri json for individual songs/tracks, and podcast id parameters to add/delete any particular songs or podcasts
#the below will not be in automation; should return a successful message and what was taken out
remove_from_daily_drive()  #takes in a name and type (e.g. "track names", "podcast/song" ) - a uri (or multiple uri json) to add individual songs/podcast episodes
#
add_to_daily_drive()


edit_podcast_list() #this function will have parameters on what to edit (add, delete, podcast_name/id [will be retrieved from txt dock, and checks if podcast is already in list - > it will do this by searching through current daily drive playlis & editing textd ock])



#*********** Above are Main Function Calls ***************#
#*********** Below are Support Function Calls ***************#

def create_daily_drive():
    return 'Starting Build'

#todo list: 
#next steps: get the basics to work. Create_daily_drive switch statements, create text documents, start with basic daily drive playlist and repopulating with my podcast choices

#see daily drive notes - get each module working as a stand alone before being called by other modules

#******PY CODE MODULES TODO ************#
# playlist, podcast, search, finish main, get image.py to work,  enhance search, enhance authcode

#******AUTH CODE STUFF TODO***************#
#1. have authtoken.py automaticlaly open authcode.py when we get an error (even from the refresh token)
#2. have authcode.py open a window and copy the url from the end anyway
#3. maybe have python open the javascript, and have javascript send the authcode back to python

#for auth code, is there a way to enbed a script in a page
#so when someone goes to said page, it runs your script?
#i can then write a script that reads the url of a given open page from specific browser
