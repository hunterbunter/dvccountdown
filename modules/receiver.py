#!/usr/bin/env python
# This file contains the modules to access and process devcoin receiver files
import urllib2, re

def GetSharesReceiverSummary():
	path = 'https://raw.github.com/Unthinkingbit/charity/master/receiver_summary.txt'
	resp = urllib2.urlopen(path)
	result = resp.read().split('\n')
	
	for row in result:
		if 'There were' in row:
			lines = re.sub('[^0-9]+', ' ', row)
	lines = lines.split(' ')
	return 180000000/int(lines[1])

def GetSharesByRound(round):
	path = 'http://d.evco.in/charity/receiver_'+str(round)+'.csv'
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
		path = 'http://d.evco.in/charity/account_'+str(round)+'.csv'
		response = urllib2.urlopen(path)
		result = response.read().split('\n')
		breakdown = {}
		sharelines = []
		for row in result:			
			if 'Shares' in row:
				sharelines.append(row)
				if 'Bitcoin Share List' in row:
					breakdown['BitcoinSL'] = re.sub("Bitcoin Share List: ", "", row)
				elif 'Bounty' in row:
					breakdown['Bounty'] = re.sub("Bounty: ", "", row)
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

		shares = 0
		for line in sharelines:
			shares += int(re.sub('[^0-9]+', '', line))		
	
		try:
			if name_round != round and name_round != None and name_round != "":
				path = 'http://d.evco.in/charity/account_'+str(name_round)+'.csv'
				response = urllib2.urlopen(path)
				result = response.read().split('\n')
		except urllib2.HTTPError:
			pass

		myshares, tally = GetSharesByName(name, name_round, result)

		return shares, breakdown, name, myshares, tally
	except urllib2.HTTPError:
		return 1, None, None, None, None
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
