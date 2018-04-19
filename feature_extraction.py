import csv

all_tweets = []
users = {}

with open('russian-troll-tweets/tweets.csv', newline='') as csvfile:
	reader = csv.DictReader(csvfile)
	for row in reader:
		all_tweets.append(row)

with open('russian-troll-tweets/users.csv', newline='') as csvfile:
	reader = csv.DictReader(csvfile)
	for row in reader:
		non_id_keys = list(row.keys())
		non_id_keys.remove('id')
		users[row['id']] = {k: row[k] for k in non_id_keys}
		users[row['id']]['tweets'] = []

for tweet in all_tweets:
	if tweet['user_id'] in users:
		users[tweet['user_id']]['tweets'].append(tweet)
	else:
		print("Unmatched tweet: "+str(tweet))
		users[tweet['user_id']] = {'tweets': [tweet]}

