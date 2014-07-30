import urllib
import urllib.request
import json
import datetime
import math
import bot_utils
import crunchbase

class Key_Attr_Check:

	def __init__( self, attrs ):
		self.attrs = attrs

	def match( self, startup ):
		m = True
		for attr in self.attrs:
			val = startup.get( attr )
			if val is None or val is False:
				m = False
				break
		return m
			
class Startup_Check:

	def match( self, startup ):
		company_type = startup.get( "company_type" )
		if company_type is None:
			return True

		if len( company_type ) == 0:
			return True

		m = False
		for t in company_type:
			if ( t.get( "name" ) == "startup" ):
				m = True
				break

		return m


al_checks = [ Startup_Check(), Key_Attr_Check( [ "name", "high_concept", "product_desc", "company_url" ] ) ]

def recent_startups( startups, url, max=1000 ):

	print( "AngelList.recent_startups => %s" % url ) 
	results = bot_utils.load_json( url )
		
	count = 0
	if results is not None:
		for al_data in results.get( "startups" ):
			if bot_utils.match_all( al_data, al_checks ):
				name = al_data.get( "name" );
				startup = create( al_data )
				crunchbase.find_startup( startup, name )
				startups.append( startup )
				print( "Found via AL: " + name )
				count = count + 1
				if count > max:
					break
	return startups;

def find_startup( name ):
	url = "https://api.angel.co/1/search?type=Startup&query=%s" % name
	
	results = bot_utils.load_json( url )
	if results is None or len( results ) == 0:
		return None

	al_id = None if results is None else results[0].get( "id" )

	if al_id is not None:
		 al_data = bot_utils.load_json( "https://api.angel.co/1/startups/%s" % al_id )
		 if al_data is not None:
		 	if bot_utils.match_all( al_data, al_checks ):
		 		startup = create( al_data )
		 		crunchbase.find_startup( startup, name )
		 		return startup

	return None

def create( al_data ):
	startup = {}
	startup[ "al_data" ] = al_data
	startup[ "name" ] = property( al_data, "name" )
	startup[ "short_description" ] = property( al_data, "high_concept" )
	startup[ "description" ] = property( al_data, "product_desc" )
	startup[ "url" ] = property( al_data, "company_url" )
	startup[ "angel_list_url" ] = property( al_data, "angellist_url" )
	startup[ "location" ] = location( al_data )
	startup[ "tags" ] = tags( al_data )
	startup[ "quality" ] = property( al_data, "quality" )

	updated = property( al_data, "updated_at" )
	bot_utils.set_if_empty( startup, "updated",  
		datetime.datetime.strptime( updated, '%Y-%m-%dT%H:%M:%SZ').replace(hour=0, minute=0, second=0, microsecond=0 ) )

	return startup
	
def property( startup, prop ):
	al_data = startup.get( "al_data" )
	if al_data is None:
		al_data = startup

	value = None
	if al_data is not None:
		value = al_data.get( prop )
	return value

def location( al_data ):
	locs = property( al_data, "locations" )
	loc = None
	if locs is not None and len( locs ) > 0:
		loc = locs[0].get( "display_name" ).lower().title()
	return loc

def tags( al_data ):
	tags = []
	markets = al_data.get( "markets" )
	if markets is not None:		
		for market in markets:
			tags.append( market.get( "name").lower() )
	return tags

