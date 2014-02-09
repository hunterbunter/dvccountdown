#!/usr/bin/env python
import json, web, urllib2, re

db = json.load(open("db.access"))
db = web.database(dbn=str(db['type']), db=str(db['name']), user=str(db['user']), pw=str(db['pass']))

def build_rating_db():

	debug = False
	if debug: print "Processing account_27"
	path = "http://raw2.github.com/Unthinkingbit/charity/master/account_27.csv"
	response = urllib2.urlopen(path).read()

	result = response.split('\n')

	rater_lines = []
	for row in result:
		if "Rater" in row:
			subrow = []
			subrow.append(row.split(',')[0])
			for item in row.split(','):
				if "Rater" in item:
					url = re.sub(r'^.*\(', "", item)
					url = re.sub(r'\)$', "", url)
					subrow.append(url)
			rater_lines.append(subrow)

	# 27 was a special case, after that it was different written
	# get round number
	if debug: print "Getting round off dvccountdown"
	path = "http://dvccountdown.blisteringdevelopers.com"
	result = urllib2.urlopen(path).read().split('\n')

	startround = 28
	endround = 28
	for row in result:
		if "<th>Round" in row:
			endround = int(re.sub(r'^.*Round ', "", row)) + 1
			break

	if debug: print "startround: %d\tround received: %d" % (startround, endround)

	for i in range(startround, endround):
		if debug: print "Processing round %d" % i
		path = "http://raw2.github.com/Unthinkingbit/charity/master/account_"+str(i)+".csv"
		try:
			result = urllib2.urlopen(path).read().split('\n')
			for row in result:
				if "Rating Comments" in row:
					subrow = []
					subrow.append(row.split(',')[0])
					for item in row.split(','):
						if "Rating Comments" in item:
							url = re.sub(r'^.*\(', "", item)
							url = re.sub(r'\)$', "", url)
							subrow.append(url)
					rater_lines.append(subrow)

		except:
			pass
	if debug:
		for row in rater_lines:
			print row
	
	if debug: print "Processing devtome rater_pages"

	t = db.transaction()
	try:
		# first clear the database
		db.query("delete from ratings")
		for rater_page in rater_lines:		
			result = urllib2.urlopen(rater_page[1]).read().split('\n')
			if debug: print "accessing %s" % rater_page[1]
			for row in result:
				if '<div class="li"><a href="http://devtome.com/doku.php?id=wiki:user:' in row:
					# get author
					author = re.sub(r'<li class="level[0,1]?"><div class="li"><a href="http://devtome.com/doku.php\?id=wiki:user:', '', row)
					author = author.split('"')[0]
					# get article_url
					article_url = re.sub(r'^.*, <a href="http://devtome.com/doku.php\?id=', "http://devtome.com/doku.php?id=", row)
					article_url = article_url.split('"')[0]
					#create the author url
					author_url = 'http://devtome.com/doku.php?id=wiki:user:'+author
					# extract the rating
					rating = re.sub(r'^.*</a>:[ ]*', "", row)
					rating = re.sub(r'[ ]*</div>', "", rating)
					rating = re.sub(r' - ', " ", rating)
					rating = rating.split(" ", 1)
					if len(rating) > 1:	comment = rating[1]
					else: comment = ""
					rating = rating[0]
				
					# store in db
					db.query("insert into ratings (rater, rater_url, author_url, article_url, author, rating, comment) values ($rater, $rater_url, $author_url, $article_url, $author, $rating, $comment)", vars={'rater':rater_page[0], 'rater_url':rater_page[1], 'author_url':author_url, 'article_url':article_url, 'author':author, 'rating':rating, 'comment':comment})
	except:
		t.rollback()
		raise
	else:
		t.commit()				

def GetRatingsByAuthor(author):
	ratings = []
	try:
		results = db.query('select * from ratings where author = $author', vars={'author':author})
		for row in results:
			ratings.append(row)
	except:
		ratings = []
		raise
	return ratings


if __name__ == "__main__":
	# run the db_update
	build_rating_db()
