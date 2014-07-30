
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

class Property_Check:

	def __init__( self, property, values ):
		self.property = property
		self.values = values

	def match( self, startup ):
		value = startup.get( self.property )
		if value is None:
			return False

		if isinstance( value, list ):
			for v in value:
				if v in self.values:
					return True
			return False
		else:
			return value in self.values

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

class Date_Check:

	def __init__( self, stop_date ):
		self.stop_date = stop_date

	def match( self, startup ):
		round = last_round( startup )
		if round is not None:
			d = property( round, "updated_at" )

			if datetime.datetime.fromtimestamp( d ) > self.stop_date:
				return True
		return False



