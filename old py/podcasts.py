#This module is for podcast manipulation
#This is where we may or may not add podcasts to the playlist




#*********** Below are Main Function Calls ***************#

add_podcast_to_playlist(playlist_id,poisiton) #calls the search for podcast uri function, and adds it playlist given posiiton (if no position, defaults to add it to the end)

get_podcast_uri() #calls the search function from search.py

get_podcast_id(podcast_name) #this will be call the function from search.py

#find podcast name given uri or playlist_id
get_podcast_name(id)

get_podcast_episode_name(uri)
get_podcast_episode_name(id)


autopopulate_podcasts(podcast_id) #adds all the podcasts in the save files into said playlist
#*********** Above are Main Function Calls ***************#