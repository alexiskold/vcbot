import json
import datetime
import locale
import angel_list
import crunchbase
import product_hunt
import bot_utils

import smtplib
from email.mime.text import MIMEText

def to_html( startups ):
	c = 0
	html = ""

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

		html = html + "<p><b>" + str( c ) + ". %s (%s)</b><br/>%s" % ( n, loc, hc )
		html = html + "<br/>" + "<a href='%s' target='_blank'>URL</a>" % ( url )

		aurl = startup.get( "angel_list_url" )
		if aurl is not None:
			q = str( angel_list.property( startup, "quality" ) )
			f = str( angel_list.property( startup, "follower_count" ) )
			html = html + "  |  <a href='%s' target='_blank'>AngelList (q=%s, f=%s)</a>" % ( str( aurl ), q, f )

		cburl = startup.get( "crunchbase_url" )
		if cburl is not None:
			html = html + "  |  <a href='%s' target='_blank'>CrunchBase</a>" % ( str( cburl ) )		
		
		total_funding = startup.get( "total_funding" )
		if total_funding is not None and total_funding != 0 :
			html = html + "<br/>" + "Funding: %s" % ( str( locale.currency( total_funding, grouping=True ) )[:-3] )

		last_round = startup.get( "last_round" )
		if last_round is not None:
			html = html + '   <a href="%s">%s: %s</a>' % ( 
				str( startup.get( "crunchbase_last_round_url" ) ),
				str( startup.get( "last_round_type" ) ),
				str( locale.currency( last_round, grouping=True ) )[:-3] )

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

def al_recent( startups, max_pages ):
	locations = [ 1664 ]

	for page in range( 1, max_pages + 1):
		angel_list.recent_startups( startups, "https://api.angel.co/1/startups?filter=raising&page=%s" % page )

	for location in locations:
		for page in range( 1, max_pages + 1):
			angel_list.recent_startups( startups, "https://api.angel.co/1/tags/%s" % location + "/startups?page=%s" % page )

	return startups

def cb_recent( startups, max_pages ):	
	for page in range( 1, max_pages + 1):
		crunchbase.recent_startups( startups, "http://www.crunchbase.com/funding-rounds?page=%s" % page )
	return startups


def ph_recent( startups, max_pages ):	
	for page in range( 1, max_pages + 1):
		product_hunt.recent_hunts( startups, "http://www.producthunt.com/?page=%s" % page )
	return startups

def recent():
	startups = []
	max_pages = 5

	cb_recent( startups, max_pages )
	#al_recent( startups, max_pages )
	#ph_recent( startups, max_pages )

	nyc_check = bot_utils.And_Check( bot_utils.Property_Check( "location", [ 'New York', 'New York City' ] ),
									 bot_utils.Num_Property_Check( "quality", 3, 1000, True ) )
	
	tags = [ 'artificial intelligence', 
			 'big data', 'big data analytics', 'predictive analytics', 
			 'bitcoin', 'payments', 'fintech', 'finance technology'
			 'connected cars', 'hardware', 'iot', 'connected home', 'internet of things', 'wearable', 'wearables','connected device', 'connected devices', 'robotics'
			 'e-commerce', 
			 'saas', 'infrastructure', 'cloud', 'enterprise software', 'search' ]
	tc = bot_utils.Property_Check( "tags", tags )
	fc = bot_utils.Num_Property_Check( "total_funding", 200000, 2000000 )
	tag_and_funding_check = bot_utils.And_Check( fc, tc )
	
	europe_and_funding_check = bot_utils.And_Check( fc, bot_utils.Property_Check( "location", 
				[ 'Paris', 'Stockholm', 'Helsinki', 'Berlin', 'Dublin', 'Ljubljana' ] ) )

	checks = [ nyc_check, tag_and_funding_check,  europe_and_funding_check ]
	return [ startup for startup in startups if bot_utils.match_one( startup, checks ) ]

def unique_tags( startups ):
	ut = set()
	for startup in startups:
		tags = startup.get( "tags" )
		for t in tags:
			ut.add( t )
	print ( sorted( ut ) )

startups = recent()

results = "<html><body>%s</body></html>" % to_html( startups )

f = open('t.html', 'w')
f.write( results )
f.close()



