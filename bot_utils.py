
import urllib
import urllib.request
import json

def load_json( url ):
	request  = urllib.request.urlopen( url )
	response = request.read()
	results = json.loads( response.decode('utf8') )
	request.close();
	return results;