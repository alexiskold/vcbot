import bot_utils
import crunchbase
import angel_list
import urllib


ph_headers = { 'User-Agent' : 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.1916.114 Safari/537.36' }


def adjust_path( name ):
	idx = name.find( '(pre-launch)' )
	if idx is not -1:
		return name[0:idx].strip()
	return name

def recent_hunts( startups, url, max=1000 ):
	print( "Product Hunt.recent_hunts => %s" % url ) 

	names = bot_utils.find_names( url, 'target="_blank">', '</a>', ph_headers )
	count = 0
	for name in names:
		startup = angel_list.find_startup( urllib.request.pathname2url( adjust_path( name ) ) )
		if startup is not None:
			startups.append( startup )
			print( "Found via PH: " + name )
			count = count + 1
			if count > max:
				break
	return startups

