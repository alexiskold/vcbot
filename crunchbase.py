import json
import urllib
import urllib.request
import datetime
import bot_utils

base_api = "http://api.crunchbase.com/v/2/"
base_web = "http://www.crunchbase.com/"
funding_web = base_web + "funding-round/"

def normalize( name ):
	return name.lower().replace( " ", "-" )

def authenticate( url ):
	return url + "?user_key=965fd081754ede59027768df720f3bf1"

def property( cb_data, property ):
	return cb_data.get( "data" ).get( "properties" ).get( property )

def relationship( cb_data, property ):
	val = cb_data.get( "data" ).get( "relationships" ).get( property )
	return None if val is None else val.get( "items" )

class Location_Check:

	def __init__( self, location_list ):
		self.location_list = location_list;

	def match( self, startup ):
		return location( startup ) in self.location_list

class Funding_Check:

	def __init__( self, raise_max, total_max ):
		self.raise_max = raise_max
		self.total_max = total_max

	def match( self, startup ):
		lr = last_round( startup )
		total = total_funding( startup )
		raised = property( lr, "money_raised_usd" );
		if raised is None:
			raised = self.raise_max + 1

		return raised < self.raise_max and total < self.total_max

class Date_Check:

	def __init__( self, stop_date ):
		self.stop_date = stop_date;

	def match( self, startup ):
		round = last_round( startup )
		if round is not None:
			d = property( round, "updated_at" )

			if datetime.datetime.fromtimestamp( d ) > self.stop_date:
				return True
		return False

def set_cb_path( startup ):
	cb_path = startup.get( "cb_path" )
	if cb_path is None:
		cb_url = startup.get( "cb_url" )
		if cb_url is not None:
			idx = cb_url.rfind( "/" )
			startup[ "cb_path" ] = cb_url[ idx: ];
			return

		startup[ "cb_path" ] = normalize( startup.get( "name" ) )

def load_cb_data( startup ):
	if startup.get( "cb_data" ) is None:
		try:
			set_cb_path( startup )
			path = startup.get( "cb_path" )
			url = authenticate( base_api + "organization/" + path )
			startup[ "cb_data" ] = bot_utils.load_json( url )
			response = startup[ "cb_data" ].get( "data" ).get( "response" )
			if response is False:
				startup[ "cb_data" ] = None	
			else:
				startup[ "crunchbase_url" ] = base_web + "organization/" + startup.get( "cb_path" )
		except:
			print( "can't load: " + startup.get( "cb_path" ) )
	return startup.get( "cb_data" )

def total_funding( startup ):
	if startup.get( "cb_total_funding" ) is None:
		cb_data = load_cb_data( startup )
		if cb_data is not None: 
			startup[ "cb_total_funding" ] = property( cb_data, "total_funding_usd" )
	return startup.get( "cb_total_funding" )

def location( startup ):
	if startup.get( "cb_location" ) is None:
		cb_data = load_cb_data( startup )
		if cb_data is not None: 
			location = relationship( cb_data, "headquarters" )
			if location is None:
				return

			cb_location = location[0].get( "country_code" )
			if cb_location == 'USA':
				cb_location = location[0].get( "city" )
			if cb_location is not None:
				cb_location = cb_location.lower()
			startup[ "cb_location" ] = cb_location
	return startup.get( "cb_location" ) 


def last_round( startup ):
	if startup.get( "cb_last_round" ) is None:
		cb_data = load_cb_data( startup )
		if cb_data is not None: 		
			rounds = relationship( cb_data, "funding_rounds" ) 
			if rounds is not None:
				round = rounds[0]
				url = authenticate( "http://api.crunchbase.com/v/2/" + round.get( "path") )
				startup[ "cb_last_round" ] = bot_utils.load_json( url )
	return startup.get( "cb_last_round" )

def sort_helper( startup ):
	last_round = startup.get( "cb_last_round" )
	val = 0
	if last_round is not None:
		val = -property( last_round, "money_raised_usd" )
	return val


def load_cb_rounds( startup ):
	if startup.get( "cb_rounds" ) is None:
		cb_data = load_cb_data( startup )
		if cb_data is not None: 
			rounds = relationship( cb_data, "funding_rounds" )
			startup[ "cb_rounds" ] = [];
			for round in rounds:
				url = authenticate( "http://api.crunchbase.com/v/2/" + round.get( "path") )
				round_data = bot_utils.load_json( url )
				startup[ "cb_rounds" ].append( round_data )
	return startup.get( "cb_rounds" )

def init_from_cb( startup ):
	cb_data = startup.get( "cb_data" )
	if cb_data is not None:
		startup[ "name" ] = property( cb_data, "name" )
		startup[ "company_url" ] = property( cb_data, "homepage_url" )
		startup[ "high_concept" ] = property( cb_data, "short_description" )
		location( startup )
		total_funding( startup )	


def recent_funding_rounds( startups, checks, url ):
	print( "Crunchbase.recent_funding_rounds => %s" % url ) 

	names = bot_utils.find_names( url, '<h4><a href="/organization/', '"', {} )
	for name in names:
		s = '{ "cb_path" : "' + name + '" }'
		startup = json.loads( s )
		load_cb_data( startup )
		if startup.get( "cb_data" ) is not None:
			ok = True
			for check in checks:
				if check.match( startup ) is False:
					ok = False
					break
			if ok:
				init_from_cb( startup )
				last_round( startup )
				startups.append( startup )
				print( "Added: " + startup.get( "cb_path" ) )
	return startups
		


