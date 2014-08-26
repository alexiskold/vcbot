import bot_utils
import crunchbase
import angel_list
import datetime
import urllib


ph_headers = { 'User-Agent' : 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.1916.114 Safari/537.36' }

def authenticate( url ):
	return url + "&access_token=f9f96f658c15bddef464f6b7457884ea47c316aa42f7509206299d4f58d9aa08"

def adjust_path( name ):
	idx = name.find( '(pre-launch)' )
	if idx is not -1:
		return name[0:idx].strip()
	return name

def recent_hunts( startups, url, max=1000 ):

	print( "Product Hunt.recent_hunts => %s" % url ) 

	ph_data = bot_utils.load_json( authenticate( url ) )
	posts = ph_data.get( "posts" )
	count = 0
	for post in posts:
		name = post.get( "name")
		startup = angel_list.find_startup( urllib.request.pathname2url( adjust_path( name ) ) )
		if startup is not None:
			startups.append( startup )
			startup[ "product_hunt_url" ] = post.get( "discussion_url" )
			startup[ "product_hunt_votes" ] = post.get( "votes_count" )
			startup[ "product_hunt_comments" ] = post.get( "comments_count" )
			startup[ "updated" ] = datetime.datetime.strptime( post.get( "day" ), '%Y-%m-%d' )
			print( "Found via PH: " + name )
			count = count + 1
			if count > max:
				break
	return startups


