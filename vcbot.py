import json
import datetime
import time
import locale
import sys
import argparse

#development only
import ipdb

#local import - needs to change to relative package import
import angel_list
import crunchbase
import product_hunt
import bot_utils
import cb_scraping

#emailing
import smtplib
from email.mime.text import MIMEText

def to_html( startups ):
	c = 0
	html = ""

	# Ehh.... its diff on 2 computers
	try:
		locale.setlocale(locale.LC_ALL, 'en_US.utf8' )
	except:
		locale.setlocale(locale.LC_ALL, 'en_US.UTF-8' )

	for startup in startups:
		c = c + 1
		
		n = startup.get( "name" )
		hc = startup.get( "short_description" )
		url = startup.get( "url" )
		loc = startup.get( "location" )
		updated = startup.get( "updated" ).strftime( '%m-%d-%Y')

		html = html + "<p><b>" + str( c ) + ". %s (%s)</b><br/>%s, updated %s" % ( n, loc, hc, updated )
		html = html + "<br/>" + "<a href='%s' target='_blank'>URL</a>" % ( url )

		aurl = startup.get( "angel_list_url" )
		if aurl is not None:
			q = str( angel_list.property( startup, "quality" ) )
			f = str( angel_list.property( startup, "follower_count" ) )
			html = html + "  |  <a href='%s' target='_blank'>AngelList (q=%s, f=%s)</a>" % ( str( aurl ), q, f )

		cburl = startup.get( "crunchbase_url" )
		if cburl is not None:
			html = html + "  |  <a href='%s' target='_blank'>CrunchBase</a>" % ( str( cburl ) )		

		phurl = startup.get( "product_hunt_url" )
		if phurl is not None:
			v = str( startup.get( "product_hunt_votes" ) )
			cm = str( startup.get( "product_hunt_comments" ) )
			html = html + "  |  <a href='%s' target='_blank'>ProductHunt (v=%s, c=%s)</a>" % ( str( phurl ), v, cm )
		
		total_funding = startup.get( "total_funding" )
		if total_funding is not None and total_funding != 0 :
			html = html + "<br/>" + "Funding: %s" % ( str( locale.currency( total_funding, grouping=True ) )[:-3] )

		last_round = startup.get( "last_round" )
		if last_round is not None:
			round_str = "%s: %s" % ( str( startup.get( "last_round_type" ) ),
				str( locale.currency( last_round, grouping=True ) )[:-3] )

			last_round_url = startup.get( "last_round_url" )
			if last_round_url is not None and len( last_round_url ) > 0:
				html = html + ('   <a href="%s">%s</a>' % 
							     ( str( startup.get( "last_round_url" ) ), round_str ) )
			else:					
				html = html + '   %s' % round_str

		tags = startup.get( "tags" )
		if len( tags ) != 0:
			html = html + "<br/>Tags: " + ', '.join( tags )

	return html

def send_email( sender, addresses, content ):
	d = datetime.datetime.strftime( datetime.datetime.today(), "%m-%d-%Y" )

	msg = MIMEText( content, 'html' )
	msg['Subject'] = d + ': startups to review'
	msg['From'] = sender
	msg['To'] = ','.join(addresses)

	s = smtplib.SMTP('localhost')
	s.sendmail( sender, addresses, msg.as_string() )
	s.quit()

def al_recent( startups, max_pages, locations ):

	for page in range( 1, max_pages + 1):
		angel_list.recent_startups( startups, "https://api.angel.co/1/startups?filter=raising&page=%s" % page )

	for location in locations:
		for page in range( 1, max_pages + 1):
			angel_list.recent_startups( startups, "https://api.angel.co/1/tags/%s" % location + "/startups?page=%s" % page )

	return startups

def cb_recent( startups, max_pages, scrap, use_cache):
	link = "https://www.crunchbase.com/funding-rounds"
	if scrap:
		# if we were to scrap the page, pass use_cache to tell whether to
		crunchbase.scrap_recent_startups( startups, link, use_cache, max_pages)
	else:
		crunchbase.recent_startups( startups, name_json )
	return startups


def ph_recent( startups, max_pages ):	
	for page in range( 0, max_pages ):
		product_hunt.recent_hunts( startups, "https://api.producthunt.com/v1/posts?days_ago=%s" % page )
	return startups

def recent( max_pages, al_location_ids, primary_locations, secondary_locations, tags ):
	startup_map = {}

	cb_recent( startup_map, max_pages, scrap=True, use_cache=True)
	# ipdb.set_trace()
	al_recent( startup_map, max_pages, al_location_ids )
	ph_recent( startup_map, max_pages )

	# In primary location criteria is looser 
	fc = bot_utils.Num_Property_Check( "total_funding", 0, 3000000 )
	qc = bot_utils.Num_Property_Check( "quality", 0, 1000 )
	funding_or_quality = bot_utils.Or_Check( fc, qc )

	primary_location_check = bot_utils.And_Check( funding_or_quality,
				bot_utils.Property_Check( "location", primary_locations ) )

	# In secondary locations, have min funding 
	fc = bot_utils.Num_Property_Check( "total_funding", 50000, 3000000 )

	secondary_location_check = bot_utils.And_Check( fc,
				bot_utils.Property_Check( "location", secondary_locations ) )

	tc = bot_utils.Property_Check( "tags", tags )
	
	tag_check = bot_utils.And_Check( fc, tc )
	
	checks = [ primary_location_check, secondary_location_check, tag_check ]

	startups = startup_map.values()
	startups = [ startup for startup in startups if bot_utils.match_one( startup, checks ) ]

	return sorted( startups, key=sort_helper )


def unique_tags( startups ):
	ut = set()
	for startup in startups:
		tags = startup.get( "tags" )
		for t in tags:
			ut.add( t )
	print ( sorted( ut ) )

def sort_helper( startup ):
	d = startup.get( "updated" )
	return - time.mktime( d.timetuple() )

def unpack_json( json_file ):
	result =  json.loads(json_file.read())
	return result

if __name__ == "__main__":

	parser = argparse.ArgumentParser(
		description='This is VCBOT!!',
		epilog="did I say, this is VCBOT!!")

	parser.add_argument('--config', metavar="[CONFIG FILE]", help="specify config file (all files must be stored under config/", default="config_ny.json", )

	parse_result = parser.parse_args(sys.argv[1:])

	config_file = "config/{0}".format(parse_result.config)

	# ipdb.set_trace()

	with open(config_file, "r") as al_location_json:
		result = unpack_json(al_location_json)
	if result != None:
		al_location = result.get("al_location")
		primary_locations = result.get("primary_locations")
		secondary_locations = result.get("secondary_locations")
		tags = result.get("tags")
		max_pages = result.get("max_pages")

	else:
		print("config.json file is not valid")
		sys.exit(1)

	# ipdb.set_trace()

	al_location_ids = al_location.values() # get location id from dictionary

	startups = recent( max_pages, al_location_ids, primary_locations, secondary_locations, tags ) # create massive dictionary

	results = "<html><body>%s</body></html>" % to_html( startups ) # convert massive dictionary to htmls

	# send_email( 'yoland.yan@techstars.com', ['alex.iskold@techstars.com', 'kj.singh@techstars.com'], results ) 


	with open('t.html', 'w') as f: 
		f.write( results )



