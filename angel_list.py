import urllib
import urllib.request
import json
import datetime
import math
import bot_utils


class Date_Check:

	def __init__( self, stop_date ):
		self.stop_date = stop_date

	def match( self, startup ):
		fundraising = startup.get( "fundraising" )
		if fundraising is not None and fundraising is not False:
			d = startup.get( "fundraising" ).get( "updated_at" );
			if d is not None and d is not False and datetime.datetime.strptime( d, "%Y-%m-%dT%H:%M:%SZ" ) > self.stop_date:
				return True

		d = startup.get( "updated_at" );
		if d is not None and d is not False and datetime.datetime.strptime( d, "%Y-%m-%dT%H:%M:%SZ" ) > self.stop_date:
			return True

		return False

class Location_Check:

	def __init__( self, location_list ):
		self.location_list = location_list;

	def match( self, startup ):
		locations = startup.get( "locations" );
		m = False
		if locations is not None:
			for location in locations:
				id = location.get( "id" )
				if id in self.location_list:
					m = True
					break
		return m

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


def recent_startups( startups, checks, url ):

	print( "AngelList.recent_startups => %s" % url ) 
	results = bot_utils.load_json( url )
		
	for startup in results.get( "startups" ):
		m = True
		for check in checks:
			if not check.match( startup ):
				m = False
				break
		if m:
			startups.append( startup )
			print( "Added: " + startup.get( "name" ) )

	return startups;

def sort_helper( startup ):
	q = startup.get( "quality" )
	if q is None:
		return 0

	f = startup.get( "follower_count" )
	if f is None:
		return 0

	return -q * math.sqrt( f )

def find_startup( name ):
	url = "https://api.angel.co/1/search?type=Startup&query=%s" % name
	
	results = bot_utils.load_json( url )
	if results is None or len( results ) == 0:
		return None

	al_id = None if results is None else results[0].get( "id" )
	if al_id is not None:
		 return bot_utils.load_json( "https://api.angel.co/1/startups/%s" % al_id )

	return None



