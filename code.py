#!/usr/bin/env python
import web
import urllib, re
import time, calendar
import json
from jsonrpc import ServiceProxy
from modules import receiver
from modules import ratings

# Uncomment this and make it false if you want to turn off browser debugging (important for release!)
#web.config.debug = False


urls = (
	'/', 'index',
	'/shares', 'shares',
	'/devtome', 'devtome',
	'/devtome/(\d+)/([a-zA-Z\d_]*)', 'devtome_round_writer',
)

app = web.application(urls, locals())
db = json.load(open("db.access"))
rpc = json.load(open("rpc.access"))
db = web.database(dbn=str(db['type']), db=str(db['name']), user=str(db['user']), pw=str(db['pass']))

if web.config.get('_session') is None:
	store = web.session.DBStore(db, 'sessions')
	session = web.session.Session(app, store, initializer={'name':0, 'round':0, 'active_page':'home'})
	web.config._session = session
else:
	session = web.config._session

# set session parameters
web.config.session_parameters.update(cookie_name="tasty_cookie", cookie_domain="blisteringdevelopers.com")

render = web.template.render('templates', base='base', globals={})

def create_render():
	return web.template.render('templates', base='base' )
		
class index:
	def GET(self):
		if session['active_page'] != "home":
			if session['active_page'] == "devtome":
				raise web.seeother('/devtome')
		rpc_daemon = ServiceProxy("http://"+rpc['user']+":"+rpc['pass']+"@blisterpool.com:52332")
		block = rpc_daemon.getinfo()['blocks']
		blocksleft = 4000 - int(block)%4000

		round = (int(block) + blocksleft)/4000

		minleft = blocksleft * 10
		h, m = divmod(minleft, 60)
		d, h = divmod(h, 24)
		timeleft = "%d days, %d hours and %d minutes" % (d, h, m)

		secondstogo = blocksleft * 600
		eta = calendar.timegm(time.gmtime()) + secondstogo
		eta = time.strftime("%a, %d %b %Y %H:%M +0000", time.gmtime(eta))

		if blocksleft > 2700: # the current payout block is still active
			activeround = round
			activeroundstart = ((round - 1) * 4000) - 2700
		else:
			activeround = round + 1
			activeroundstart = (round * 4000) - 2700
		activeroundend = activeroundstart + 4000

		breakdown, name, myshares, tally = receiver.GetShareEstimate(activeround, session.name, session.round)
		if activeround == round:
			breakdown2 = breakdown
		else:
			breakdown2 = receiver.GetBreakdown(round)
		breakdown3 = receiver.GetBreakdown(round-1)
		if breakdown != None:
			shares = breakdown['TotalShares']
		else:
			shares = 1
		activepayout = 180000000/shares
		
		activeblocksleft = activeroundend - int(block)
		activeminleft = activeblocksleft * 10
		h, m = divmod(activeminleft, 60)
		d, h = divmod(h, 24)
		activetimeleft = "%d days, %d hours and %d minutes" % (d, h, m)

		activesecondstogo = activeblocksleft * 600
		activeendtime = calendar.timegm(time.gmtime()) + activesecondstogo
		activeendtime = time.strftime("%a, %d %b %Y %H:%M +0000", time.gmtime(activeendtime))

		devpershare = receiver.GetSharesByRound(round)

		prev = {}
		prev['round'] = round - 1
		prev['devpershare'] = receiver.GetSharesByRound(round - 1)

		return render.index(name, myshares, tally, session.round, block, round, blocksleft, timeleft, eta, activeround, activepayout, activeroundstart, activeroundend, activeendtime, activetimeleft, devpershare, breakdown, breakdown2, breakdown3, prev) 

class shares:
	def POST(self):
		name, round = web.input().name, web.input().round
		session['name'] = name
		session['round'] = round
		session['active_page'] = "home"
		raise web.seeother("/")

class devtome:
	def GET(self):
		try:
			if session.name == 0:
				session.name = ""
				session.round = 22
			devtome_stats, tally = receiver.GetRatings(session.name, session.round)
			session.active_page = "home"
		except:
			raise
		try:
			results = []
			results = ratings.GetRatingsByAuthor(session.name.lower())
		except:
			raise

		return render.devtome(session.name, session.round, devtome_stats, tally, results)
	def POST(self):
		name, round = web.input().name, web.input().round
		session['name'] = name
		session['round'] = round
		session['active_page'] = "devtome"
		raise web.seeother("/devtome")

class devtome_round_writer:
	def GET(self, round, name):
		results = []
		try:
			results = ratings.GetRatingsByAuthor(name.lower())
		except: 
			raise
		try:	
			devtome_stats, tally = receiver.GetRatings(name, round)
		except:
			devtome_stats, tally = receiver.GetRatings("", 22)
		return render.devtome(name, round, devtome_stats, tally, results)

if __name__ == "__main__":
	web.wsgi.runwsgi = lambda func, addr=None: web.wsgi.runfcgi(func, addr)
	app.run()
