
import urllib
import urllib.request
import json

def load_json( url ):
	results = None
	try:
		request  = urllib.request.urlopen( url )
		response = request.read()
		results = json.loads( response.decode('utf8') )
		request.close()
	except:
		print( "Can't load: " + url )	
	return results

def load_url( url, hdrs=None ):
	request = urllib.request.Request( url, headers=hdrs )
	url_request = urllib.request.urlopen( request );
	response = str( url_request.read(), encoding='utf8' )
	url_request.close()
	return response

def find_names( page_url, anchor_start, anchor_stop, hdrs=None ):
	response = load_url( page_url, hdrs )
	l = len( anchor_start )
	l2 = len( anchor_stop )
	names = []

	idx_start = 0
	while idx_start != -1:
		idx_start = response.find( anchor_start, idx_start )
		if idx_start != -1:
			idx_end = response.find( anchor_stop, idx_start + l )
			name = response[ idx_start + l : idx_end ]
			idx_start = idx_end + l2
			names.append( name )

	return names