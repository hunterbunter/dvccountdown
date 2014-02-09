#!/usr/bin/env python
# This file contains the modules to access and process devcoin receiver files
from jsonrpc import ServiceProxy
import urllib2, re, json

#def GetSharesReceiverSummary():
#	path = 'https://raw.github.com/Unthinkingbit/charity/master/receiver_summary.txt'
#	resp = urllib2.urlopen(path)
#	result = resp.read().split('\n')
#	
#	for row in result:
#		if 'There were' in row:
#			lines = re.sub('[^0-9]+', ' ', row)
#	lines = lines.split(' ')
#	return 180000000/int(lines[1])

def GetSharesByRound(round):
	path = 'http://dvccountdown.blisteringdevelopers.com/receiver_'+str(round)+'.csv'
	response = urllib2.urlopen(path)
	result = response.read().split('\n')
	count = -1 # to ignore the _begincoins line
	countflag = False
	for row in result:
		if "_begincoins" in row:
			countflag = True
		elif "_endcoins" in row:
			countflag = False
		if countflag == True:
			count += 1
	return 180000000/count

def GetShareEstimate(round, name, name_round):
	try:
		if name_round == None or name_round <= 0 or name_round == "":
			name_round = 3
		try:
			path = 'http://dvccountdown.blisteringdevelopers.com/account_'+str(round)+'.csv'
			response = urllib2.urlopen(path)
			result = response.read().split('\n')
			breakdown = {}
			breakdown['BitcoinSL'] = "0 Shares"
			breakdown['Bounty'] = "0 Shares"
			breakdown['BusinessBounty'] = "0 Shares"
			breakdown['DevcoinSL'] = "0 Shares"
			breakdown['Devtome'] = "0 Shares"
			breakdown['Marketing'] = "0 Shares"
			breakdown['Rating'] = "0 Shares"
			breakdown['Admin'] = "0 Shares"
			breakdown['TotalShares'] = 0
			for row in result:			
				if 'Shares' in row:
					breakdown['TotalShares'] += int(re.sub('[^0-9]+', '', row))		
					if 'Bitcoin Share List' in row:
						breakdown['BitcoinSL'] = re.sub("Bitcoin Share List: ", "", row)
					elif 'Bounty' in row and not 'Business' in row:
						breakdown['Bounty'] = re.sub("Bounty: ", "", row)
					elif 'Business' in row:
						breakdown['BusinessBounty'] = re.sub("Business Bounty: ", "", row)
					elif 'Devcoin Share List' in row:
						breakdown['DevcoinSL'] = re.sub("Devcoin Share List: ", "", row)
					elif 'Devtome Earnings' in row:
						breakdown['Devtome'] = re.sub("Devtome Earnings: ", "", row)
					elif 'Marketing Earnings' in row:
						breakdown['Marketing'] = re.sub("Marketing Earnings: ", "", row)
					elif 'Rating Earnings' in row:
						breakdown['Rating'] = re.sub("Rating Earnings: ", "", row)
					elif 'Administrator' in row:
						breakdown['Admin'] = re.sub("Administrator Bonus: ", "", row)
		except urllib2.HTTPError:
			breakdown = None
		try:
			if name_round != round and name_round != None and name_round != "":
				path = 'http://dvccountdown.blisteringdevelopers.com/account_'+str(name_round)+'.csv'
				response = urllib2.urlopen(path)
				result = response.read().split('\n')
			myshares, tally = GetSharesByName(name, name_round, result)
		except urllib2.HTTPError:
			myshares = []
			tally = 0	


		return breakdown, name, myshares, tally
	except:
		raise


def GetSharesByName(name, round, result):
	try:
		if name == None or name == 0:
			return [], 0.0
		step1 = ""
		for row in result:
			if name+',' in row or name.capitalize()+',' in row or name.lower()+',' in row.lower() or name == "":
				step1 += str(row)+','
		step1 = step1.split(',')
		myshares = []
		for row in step1:
			if re.match(r'^\d+(/5)?-', row):
				myshares.append(row)
		tally = 0.0
		for row in myshares:
			try:
				tally += float(re.sub(r'-.*', "", row))
			except ValueError:
				numerator = float(re.match(r'^\d+', row).group())
				tally += numerator/5
		# now break down myshares into lists of 2 sublists - what the payment was for, and a link if available
		for i in range(len(myshares)):
			subrow = []
			subrow.append(re.sub(r'\(.*\)', "", myshares[i]))
			try:
				subrow.append(re.search(r'\(.*\)', myshares[i]).group())	
				subrow[1] = re.sub(r'\(', "", subrow[1])
				subrow[1] = re.sub(r'\)', "", subrow[1])
			except: 
				subrow.append(None)
			myshares[i] = subrow
			

		return myshares, tally
	except urllib2.HTTPError:
		return [], 0.0	
	except:
		raise

def GetRatings(name, round):
	try:
		if name == None or name == 0:
			return None
		path = 'http://dvccountdown.blisteringdevelopers.com/devtome_'+str(round)+'.csv'
		response = urllib2.urlopen(path)
		result = response.read().split('\n')
		namelist = []
		for i in range(len(result)):
			subrow = []
			if name in result[i] or name.capitalize() in result[i] or name.lower() in result[i].lower() or i == 0:
				row = result[i].split(',')
				for item in row:
					subrow.append(item)
				if len(subrow) < 26:
					fillers = 26 - len(subrow)
					for i in range(fillers):
						subrow.append("")
				namelist.append(subrow)
		if name == "":
			tally = len(namelist)-6
		else:
			tally = len(namelist)-1
		# add devtome links to names
		for i in range(len(namelist)):
			if namelist[i][0] != "Name" and namelist[i][0] != "":
				url = '<a href="http://devtome.com/doku.php?id=wiki:user:'+str(namelist[i][0])+'">'+str(namelist[i][0])+'</a>'+' <a href="/devtome/'+round+'/'+str(namelist[i][0])+'">(Ratings)</a>'
				namelist[i][0] = url	
		return namelist, tally 
	except urllib2.HTTPError:
		return None, 0
	except:
		raise

def GetBreakdown(round):
	try:
		if round == None or round <= 3 or round == "":
			name_round = 3
		try:
			path = 'http://dvccountdown.blisteringdevelopers.com/account_'+str(round)+'.csv'
			response = urllib2.urlopen(path)
			result = response.read().split('\n')
			breakdown = {}
			breakdown['BitcoinSL'] = "0 Shares"
			breakdown['Bounty'] = "0 Shares"
			breakdown['BusinessBounty'] = "0 Shares"
			breakdown['DevcoinSL'] = "0 Shares"
			breakdown['Devtome'] = "0 Shares"
			breakdown['Marketing'] = "0 Shares"
			breakdown['Rating'] = "0 Shares"
			breakdown['Admin'] = "0 Shares"
			breakdown['TotalShares'] = 0
			for row in result:			
				if 'Shares' in row:
					breakdown['TotalShares'] += int(re.sub('[^0-9]+', '', row))							
					if 'Bitcoin Share List' in row:
						breakdown['BitcoinSL'] = re.sub("Bitcoin Share List: ", "", row)
					elif 'Bounty' in row and not 'Business' in row:
						breakdown['Bounty'] = re.sub("Bounty: ", "", row)
					elif 'Business' in row:
						breakdown['BusinessBounty'] = re.sub("Business Bounty: ", "", row)
					elif 'Devcoin Share List' in row:
						breakdown['DevcoinSL'] = re.sub("Devcoin Share List: ", "", row)
					elif 'Devtome Earnings' in row:
						breakdown['Devtome'] = re.sub("Devtome Earnings: ", "", row)
					elif 'Marketing Earnings' in row:
						breakdown['Marketing'] = re.sub("Marketing Earnings: ", "", row)
					elif 'Rating Earnings' in row:
						breakdown['Rating'] = re.sub("Rating Earnings: ", "", row)
					elif 'Administrator' in row:
						breakdown['Admin'] = re.sub("Administrator Bonus: ", "", row)
	
		except urllib2.HTTPError:
			breakdown = None
		return breakdown 
	except:
		raise

# every hour, run this to get the latest account file from d.evco.in
def UpdateFiles():
	rpc = json.load(open("rpc.access"))
	rpc_daemon = ServiceProxy("http://"+rpc['user']+":"+rpc['pass']+"@blisterpool.com:52332")
	block = rpc_daemon.getinfo()['blocks']
	blocksleft = 4000 - int(block)%4000
	current_round = (int(block) + blocksleft)/4000
	#print "current_round = %d" % current_round
	if blocksleft <= 2700: # the current payout block is still active
                        current_round += 1
	#print "current_round = %d" % current_round

	for round in range(current_round-1, current_round+1):
		try:
			# Now we know the round, we know which file to get
			path = 'http://d.evco.in/charity/receiver_'+str(round)+'.csv'
			#print "Attempting %s" % path
			f = urllib2.urlopen(path)
			data = f.read()
			with open("/home/amit/devcoin_countdown/www/static/receiver_"+str(round)+".csv", 'wb') as code:
				code.write(data)
		except:
			pass
		try:			
			path = 'http://d.evco.in/charity/account_'+str(round)+'.csv'
			#print "Attempting %s" % path
			f = urllib2.urlopen(path)
			data = f.read()
			with open("/home/amit/devcoin_countdown/www/static/account_"+str(round)+".csv", 'wb') as code:
				code.write(data)
		except:
			pass
		try:
			path = 'http://d.evco.in/charity/devtome_'+str(round)+'.csv'
			#print "Attempting %s" % path
			f = urllib2.urlopen(path)
			data = f.read()
			with open("/home/amit/devcoin_countdown/www/static/devtome_"+str(round)+".csv", 'wb') as code:
				code.write(data)
		except:
			pass		

if __name__ == "__main__":
	UpdateFiles()

