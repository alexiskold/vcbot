import bot_utils
import angel_list
import datetime
import urllib

def authenticate( url ):
	return url + "&access_token=f9f96f658c15bddef464f6b7457884ea47c316aa42f7509206299d4f58d9aa08"

def adjust_path( name ):
	idx = name.find( '(pre-launch)' )
	if idx is not -1:
		return name[0:idx].strip()
	return name

def recent_hunts( startup_map, url, max=1000 ):

	print( "Product Hunt.recent_hunts => %s" % url ) 

	ph_data = bot_utils.load_json( authenticate( url ) )
	posts = ph_data.get( "posts" )
	count = 0
	for post in posts:
		name = post.get( "name" )
		if startup_map.get( name ) is None:
			startup = angel_list.find_startup( urllib.request.pathname2url( adjust_path( name ) ) )
			if startup is not None:
				startup_map[ name ] = startup
				startup[ "product_hunt_url" ] = post.get( "discussion_url" )
				startup[ "product_hunt_votes" ] = post.get( "votes_count" )
				startup[ "product_hunt_comments" ] = post.get( "comments_count" )
				startup[ "updated" ] = datetime.datetime.strptime( post.get( "day" ), '%Y-%m-%d' )
				print( "Found via PH: " + name )
				count = count + 1
				if count > max:
					break
	return startup_map


