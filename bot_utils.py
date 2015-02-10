
import urllib
import urllib.request
import requests
import datetime
import json
import traceback

def load_json( url ):
	results = None
	try:
		response = requests.get( url )
		results = response.json()
	except Exception as e:
		print("Url: {0}".format(url))
		print("Error: {0}".format(e))
		print( "Can't load: " + url )	
	return results

def load_url( url, hdrs=None ):
	response = ""
	try:
		request = urllib.request.Request( url, headers=hdrs )
		url_request = urllib.request.urlopen( request );
		response = str( url_request.read(), encoding='utf8' )
		url_request.close()
	except:
		traceback.print_exc();
		print( "Can't load: " + url )	
	return response

def find_names( page_url, anchor_start, anchor_stop, hdrs=None ):
	response = load_url( page_url, hdrs )

	l = len( anchor_start )
	l2 = len( anchor_stop )
	names = set()

	idx_start = 0
	while idx_start != -1:
		idx_start = response.find( anchor_start, idx_start )
		if idx_start != -1:
			idx_end = response.find( anchor_stop, idx_start + l )
			name = response[ idx_start + l : idx_end ]
			idx_start = idx_end + l2
			names.add( name )

	return list( names )

def match_all( data, checks ):
	for check in checks:
		if check.match( data ) is False:
			return False
	return True

def match_one( data, checks ):
	for check in checks:
		if check.match( data ) is True:
			return True
	return False

def set_if_empty( data, prop, value ):
	cvalue = data.get( prop )
	if cvalue is None:
		data[ prop ] = value

def append_values( data, prop, values ):
	if values is None:
		return

	cvalues = data.get( prop )
	if cvalues is not None:
		data[ prop ] = cvalues + values
	else:
		data[ prop ] = values

def create_date( str ):
	updated = datetime.datetime.fromtimestamp( int( str ) )
	return updated.replace(hour=0, minute=0, second=0, microsecond=0)

class Property_Check:

	def __init__( self, property, values ):
		self.property = property
		self.values = [ x.lower() for x in values ]

	def match( self, startup ):
		value = startup.get( self.property )
		if value is None:
			return False

		if isinstance( value, list ):
			for v in value:
				if v.lower() in self.values:
					return True
			return False
		else:
			return value.lower() in self.values

class And_Check:

	def __init__( self ):
		self.checks = []

	def __init__( self, check1, check2 ):
		self.checks = [ check1, check2 ]

	def add_check( check ):
		self.checks.append( check )

	def match( self, startup ):
		for check in self.checks:
			if check.match( startup ) is False:
				return False
		return True

class Or_Check:

	def __init__( self ):
		self.checks = []

	def __init__( self, check1, check2 ):
		self.checks = [ check1, check2 ]

	def add_check( check ):
		self.checks.append( check )

	def match( self, startup ):
		for check in self.checks:
			if check.match( startup ):
				return True
		return False

class Num_Property_Check:

	def __init__( self, property_name, min_value, max_value, allow_empty=False ):
		self.min_value = min_value
		self.max_value = max_value
		self.property_name = property_name
		self.allow_empty = allow_empty

	def match( self, startup ):
		value = startup.get( self.property_name )
		if value is None:
			return self.allow_empty

		return value >= self.min_value and value < self.max_value

if __name__ == "__main__":
	result = load_json( "https://api.producthunt.com/v1/posts?days_ago=0&access_token=f9f96f658c15bddef464f6b7457884ea47c316aa42f7509206299d4f58d9aa08" )
	print(result)

