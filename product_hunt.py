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

def recent_hunts( startups, checks, url ):
	print( "Product Hunt.recent_hunts => %s" % url ) 

	names = bot_utils.find_names( url, 'target="_blank">', '</a>', ph_headers )
	for name in names:
		startup = angel_list.find_startup( urllib.request.pathname2url( adjust_path( name ) ) )
		if startup is not None:
			ok = True
			for check in checks:
				if check.match( startup ) is False:
					ok = False
					break
			if ok:
				startups.append( startup )
				print( "Added: " + name )
	return startups

