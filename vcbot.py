import json
import datetime
import locale
import angel_list
import crunchbase
import product_hunt
import threading

import smtplib
from email.mime.text import MIMEText

def to_html( startups ):
	c = 0
	html = ""

	locale.setlocale(locale.LC_ALL, 'en_US.utf8')

	for startup in startups:
		c = c + 1
		
		n = str( startup.get( "name" ) )
		hc = str( startup.get( "high_concept" ) )
		url = str( startup.get( "company_url" ) )
		loc = startup.get( "cb_location" )

		if loc is None:
			loc = startup.get( "locations" )
			if ( loc is not None ):
				loc = loc[ 0 ].get( "display_name" ).lower();
		loc = str( loc ).title()
		
		html = html + "<p><b>" + str( c ) + ". %s (%s)</b><br/>%s" % ( n, loc, hc )
		html = html + "<br/>" + "<a href='%s' target='_blank'>URL</a>" % ( url )

		aurl = startup.get( "angellist_url" )
		if aurl is not None:
			q = str( startup.get( "quality" ) )
			f = str( startup.get( "follower_count" ) )
			html = html + "  |  <a href='%s' target='_blank'>AngelList (q=%s, f=%s)</a>" % ( str( aurl ), q, f )

		cburl = startup.get( "crunchbase_url" )
		if cburl is not None:
			html = html + "  |  <a href='%s' target='_blank'>CrunchBase</a>" % ( str( cburl ) )		
		
		total_funding = startup.get( "cb_total_funding" )
		if total_funding is not None and total_funding != 0 :
			html = html + "<br/>" + "Funding: %s" % ( str( locale.currency( total_funding, grouping=True ) )[:-3] )

		last_round = startup.get( "cb_last_round" )
		if last_round is not None:
			money_raised = crunchbase.property( last_round, "money_raised_usd" )
			if money_raised is not None:
				html = html + '   <a href="%s">%s: %s</a>' % ( 
					str( crunchbase.funding_web + crunchbase.property( last_round, "permalink" ) ),
					str( crunchbase.property( last_round, "funding_type" ) ),
					str( locale.currency( money_raised, grouping=True ) )[:-3] )

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

def sort_helper( startup ):
	val = crunchbase.sort_helper( startup )
	if val == 0:
		val = angel_list.sort_helper( startup )
	return val

def al_recent( startups, d, max_pages ):
	#locations = [ 1664, 1842, 2320, 1870, 1853 ]
	locations = [ 1664 ]
	lc = angel_list.Location_Check( locations )
	dc = angel_list.Date_Check( d )
	ac = angel_list.Key_Attr_Check( [ "name", "high_concept", "product_desc", "company_url" ] )
	sc = angel_list.Startup_Check();

	for page in range( 1, max_pages + 1):
		angel_list.recent_startups( startups, [ ac, sc, lc, dc ], "https://api.angel.co/1/startups?filter=raising&page=%s" % page )

	for location in locations:
		for page in range( 1, max_pages + 1):
			angel_list.recent_startups( startups, [ ac, sc, dc ], "https://api.angel.co/1/tags/%s" % location + "/startups?page=%s" % page )

	return startups

def cb_recent( startups, d, max_pages ):	
	#fc = crunchbase.Funding_Check( 2000000, 2000000 )
	dc = crunchbase.Date_Check( d )
	#['new york', 'new york city', 'france', 'sweden', 'finland', 'spain']
	lc = crunchbase.Location_Check( ['new york', 'new york city' ] )
	for page in range( 1, max_pages + 1):
		crunchbase.recent_funding_rounds( startups, [ dc, lc ], "http://www.crunchbase.com/funding-rounds?page=%s" % page )
	return startups


def ph_recent( startups, d, max_pages ):	
	#locations = [ 1664, 1842, 2320, 1870, 1853 ]
	locations = [ 1664 ]
	lc = angel_list.Location_Check( locations )
	for page in range( 1, max_pages + 1):
		product_hunt.recent_hunts( startups, [ lc ], "http://www.producthunt.com/?page=%s" % page )
	return startups

def recent():
	startups = []
	days_ago=7
	max_pages = 5
	d = datetime.datetime.today() - datetime.timedelta( days=days_ago )

	cb_recent( startups, d, max_pages )
	al_recent( startups, d, max_pages )
	ph_recent( startups, d, max_pages )

	for startup in startups:
		crunchbase.total_funding( startup )
		crunchbase.last_round( startup )

	return startups

startups = recent()

results = "<html><body>%s</body></html>" % to_html( startups )
send_email( 'alex.iskold@techstars.com', [ 'alex.iskold@techstars.com', 'kj.singh@techstars.com'], results )

f = open('t.html', 'w')
f.write( results )
f.close()


