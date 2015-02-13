import json
import urllib
import urllib.request
import re
import datetime
import bot_utils
import cb_scraping
import ipdb


base_api = "http://api.crunchbase.com/v/2/"
base_web = "http://www.crunchbase.com/"
funding_web = base_web + "funding-round/"

def scrap_recent_startups( startup_map, url, use_cache, max_page, max_startup=1000):
	if use_cache:
		with open("cb_funding_rounds.html", "r") as page_source:
			page = page_source.read()
	else:
		page = cb_scraping.get_cb_content( url, "cb_funding_rounds.html", max_page)

	names = re.findall('<h4><a title=.*? href="/organization/(.*?)"', page)

	# ipdb.set_trace()

	count = 0
	for name in names:
		startup = {}
		if startup_map.get( name ) is None and find_startup( startup, name ):
				startup_map[ name ] = startup
				print( "Found via CB: " + name )
				count = count + 1
				if count > max_startup:
					break
	return startup_map

def recent_startups( startups_map, input_json ):
	"""If the name/uuids are given then use this instead of scrapping the page"""
	pass

def find_startup( startup, name ):
	if startup.get( "cb_data" ) is not None:
		return True

	path = name.lower().replace( " ", "-" ).replace( ".", "-")
	url = authenticate( base_api + "organization/" + path )
	cb_data = bot_utils.load_json( url )
	if cb_data is not None:
		response = cb_data.get( "data" ).get( "response" )
		if response is not False and cb_data.get( "data" ).get( "properties" ).get( "primary_role" ) == 'company':
			fill( startup, cb_data, name )			
			return True

	return False


def fill( startup, cb_data, name ):
	if startup.get( "cb_data" ) is None:
		startup[ "cb_data" ] = cb_data
		bot_utils.set_if_empty( startup, "name", property( startup, "name" ) )
		bot_utils.set_if_empty( startup, "short_description", property( startup, "short_description" ) )
		bot_utils.set_if_empty( startup, "description", property( startup, "description" ) )
		bot_utils.set_if_empty( startup, "url", property( startup, "homepage_url" ) )
		startup[ "crunchbase_url" ] = base_web + "organization/" + name.lower().replace( " ", "-" ).replace( ".", "-")
		bot_utils.set_if_empty( startup, "location", location( startup )  )
		bot_utils.append_values( startup, "tags", tags( startup ) )
		bot_utils.set_if_empty( startup, "total_funding", property( startup, "total_funding_usd" ) )
		updated = property( startup, "updated_at" )
		updated = bot_utils.create_date( updated )
		bot_utils.set_if_empty( startup, "updated",  updated )
		last_round( startup )

	return startup

def last_round( startup ):
	if startup.get( "last_round" ) is None:
		rounds = relationship( startup, "funding_rounds" ) 
		if rounds is not None:
			round = rounds[0]
			url = authenticate( "http://api.crunchbase.com/v/2/" + round.get( "path" ) )
			last_round_data = bot_utils.load_json( url )
			startup[ "cb_last_round" ] = last_round_data
			bot_utils.set_if_empty( startup, "last_round", property( startup, "money_raised_usd", "cb_last_round" ) )
			bot_utils.set_if_empty( startup, "last_round_type", property( startup, "funding_type", "cb_last_round" ) )
			bot_utils.set_if_empty( startup, "last_round_url", funding_web + property( startup, "permalink", "cb_last_round" ) )

def authenticate( url ):
	return url + "?user_key=965fd081754ede59027768df720f3bf1"

def property( startup, property, data="cb_data" ):
	target_data = startup.get( data )
	if target_data is None:
		return None

	return target_data.get( "data" ).get( "properties" ).get( property )

def relationship( startup, property, data="cb_data" ):
	target_data = startup.get( data )
	if target_data is None:
		return None

	val = target_data.get( "data" ).get( "relationships" ).get( property )
	return None if val is None else val.get( "items" )

def location( startup ):
	headquarters = relationship( startup, "headquarters" )
	if headquarters is None:
		return None

	loc = headquarters[0].get( "city" )
	if loc is None:
		loc = "none"

	country = headquarters[0].get( "country_code" )
	if 	country != 'USA' and country is not None:
		loc = country
	return loc.lower().title()

def tags( startup ):
	tags = []
	categories = relationship( startup, "categories" )
	if categories is not None:
		for category in categories:
			tags.append( category.get( "name" ).lower() )
	return tags


if __name__ == "__main__":
	startups = {}
	scrap_recent_startups(startups, "https://www.crunchbase.com/funding-rounds", False, max=10)
	print(startups)

