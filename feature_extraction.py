import re
import csv
import pickle
import nltk
import collections
import random
import numpy as np
from nltk.stem import WordNetLemmatizer
from nltk.corpus import stopwords
from tqdm import tqdm
import calendar
import time

def save_obj(obj, name):
    with open('/Users/manewilliams/Desktop/School/Cis519/Project/'+ name + '.pkl', 'wb') as f:
        pickle.dump(obj, f, pickle.HIGHEST_PROTOCOL)

def load_obj(name):
    with open('/Users/manewilliams/Desktop/School/Cis519/Project/' + name + '.pkl', 'rb') as f:
        return pickle.load(f)

common_words = set(stopwords.words('english'))
wnlemma = WordNetLemmatizer()

all_bot_tweets = []
all_ppl_tweets = []

final_embeddings = load_obj('final_embeddings')
reverse_dict = load_obj('reverse_dictionary')
word2vec_dict = load_obj('word2vec_dictionary')

# num_tweets = 0

# Extract all tweets from the csv file
with open('russian-troll-tweets/tweets.csv', newline='') as csvfile:
	reader = csv.DictReader(csvfile)
	for row in reader:
		all_bot_tweets.append(row)
		# if num_tweets >= 10:
		# 	break
		# else:
		# 	num_tweets += 1

# num_tweets = 0

with open('organic_tweets.csv', newline='') as csvfile:
	reader = csv.DictReader(csvfile)
	for row in reader:
		all_ppl_tweets.append(row)
		# if num_tweets >= 10:
		# 	break
		# else:
		# 	num_tweets += 1
# print(all_tweets[0])

# min_date_ms = None
# min_date = None
# max_date_ms = None
# max_date = None
# for tweet in all_tweets:
# 	if tweet['created_at'] != "" and (min_date_ms == None or tweet['created_at'] < min_date_ms):
# 		min_date_ms = tweet['created_at']
# 		min_date = tweet['created_str']
# 	if max_date_ms == None or tweet['created_at'] > max_date_ms:
# 		max_date_ms = tweet['created_at']
# 		max_date = tweet['created_str']
# print("Min: "+str(min_date))
# print(min_date_ms)
# print("Max: "+str(max_date))
# print(max_date_ms)

# Change tweet text bodies to bags of word2vecs
# Start by discovering word vector values by processing all tweet text combined

print("Collecting tweet text bodies...")

all_tweet_text = ""
for tweet in all_bot_tweets:
	all_tweet_text += tweet['text']
for tweet in all_ppl_tweets:
	all_tweet_text += tweet['text']


def tweet2vec(text):
	num_other_at = 0
	num_hashtags = 0
	avg_hashtag = None
	num_links = 0
	num_words = 0
	avg_word = None
	pieces = text.split(' ')
	for piece in pieces:
		if piece == '':
			continue
		elif piece[0] == '@':
			num_other_at += 1
		elif piece[0] == '#':
			num_hashtags += 1
			word = piece[1:]
			if word in word2vec_dict.keys():
				vec = final_embeddings[word2vec_dict[word]]
			else:
				vec = final_embeddings[0] # Use the value of the UNK token
			if avg_hashtag is None:
				avg_hashtag = vec
			else:
				avg_hashtag = [x + y for x, y in zip(avg_hashtag, vec)]
		elif piece[0:4] == 'http':
			num_links += 1
		else:
			word_tok = re.split('\W+', piece)
			for word in word_tok:
				num_words += 1
				if word in word2vec_dict.keys():
					vec = final_embeddings[word2vec_dict[word]]
				else:
					vec = final_embeddings[0] # Use the value of the UNK token
				if avg_word is None:
					avg_word = vec
				else:
					avg_word = [x + y for x, y in zip(avg_word, vec)]
	if avg_hashtag is None:
		avg_hashtag = final_embeddings[0] # Use the value of the UNK token
	else:
		avg_hashtag = [x / num_hashtags for x in avg_hashtag]
	if avg_word is None:
		avg_word = final_embeddings[0] # Use the value of the UNK token
	else:
		avg_word = [x / num_words for x in avg_word]
	to_ret = [num_other_at, num_hashtags]
	# to_ret.extend(avg_hashtag)
	to_ret.extend([num_links, num_words])
	to_ret.extend(avg_word)
	# print("Result of tweet2vec:")
	# print(to_ret)
	return to_ret

# Takes a tweet text and converts it to a more meaningful feature vector 
# for input to the learning algorithm
def process_tweet(text):
	index = 0
	retweet = 0
	if len(text) > 4 and text[0:2] == "RT":
		retweet = 1
		index = 4
		while index < len(text) and text[index] != ' ':
			index += 1
		rt_at = text[4:index]
	if index == len(text):
		feature = [retweet, 0, 0]
		# feature.extend(final_embeddings[0])
		feature.extend([0, 0])
		feature.extend(final_embeddings[0])
		return feature;
	text = text[index:]
	to_ret = [retweet] + tweet2vec(text)
	# print("Result of process_tweet:")
	# print(to_ret)
	return to_ret


def avg_tweets(new_tweet, prev_tweets, prev_num):
	if new_tweet is None or prev_tweets is None:
		return None
	running_avg = new_tweet
	index = 0
	while index < len(running_avg):
		running_avg[index] += (prev_num * prev_tweets[index])
		running_avg[index] /= (prev_num + 1)
		index += 1
	return running_avg
	
users = {}
organic_num_tweets = {}
bots = {}
bot_num_tweets = {}

print("Extracting tweet features...")

# Add all extracted and processed tweets to their corresponding user
# A running average is calculated at each step to avoid having all tweet vectors 
# in memory at once (which would entail a 10+gb object)
for tweet in tqdm(all_ppl_tweets):
	key = tweet['user_key'].lower()
	if key not in users or users[key] is None:
		tweet_text = process_tweet(tweet['text'])
		users[key] = tweet_text
		organic_num_tweets[key] = 1
	else:
		tweet_text = process_tweet(tweet['text'])
		users[key] = avg_tweets(tweet_text, users[key], organic_num_tweets[key])
		organic_num_tweets[key] += 1

for tweet in tqdm(all_bot_tweets):
	key = tweet['user_key'].lower()
	if key not in bots or bots[key] is None:
		tweet_text = process_tweet(tweet['text'])
		bots[key] = tweet_text
		bot_num_tweets[key] = 1
	else:
		tweet_text = process_tweet(tweet['text'])
		bots[key] = avg_tweets(tweet_text, bots[key], bot_num_tweets[key])
		bot_num_tweets[key] += 1

organic_user_data = {}
bot_user_data = {}

print("Extracting user data...")

# Extract all user data from csv file
with open('russian-troll-tweets/users.csv', newline='') as csvfile:
	reader = csv.DictReader(csvfile)
	for row in reader:
		non_id_keys = list(row.keys())
		non_id_keys.remove('screen_name')
		bot_user_data[row['screen_name'].lower()] = {k: row[k] for k in non_id_keys}

with open('organic_users.csv', newline='') as csvfile:
	reader = csv.DictReader(csvfile)
	for row in reader:
		non_id_keys = list(row.keys())
		non_id_keys.remove('screen_name')
		organic_user_data[row['screen_name'].lower()] = {k: row[k] for k in non_id_keys}

save_obj(organic_user_data, 'organic_user_data')
save_obj(bot_user_data, 'bot_user_data')
save_obj(users, 'users_origin')
save_obj(bots, 'bots_origin')
# organic_user_data = load_obj('organic_user_data')
# bot_user_data = load_obj('bot_user_data')
# users = load_obj('users_origin')
# bots = load_obj('bots_origin')

print("Generating final features...")

to_del = []

# Add additional profile data to respective bots/user features
for user, user_tweets in tqdm(users.items()):
	extra_data = []
	key = user.lower()
	if key in organic_user_data:
		profile = organic_user_data[key]
		get_time = lambda ts: calendar.timegm(time.strptime(ts,'%a %b %d %H:%M:%S +0000 %Y'))
		if profile['favourites_count'] == '' or profile['favourites_count'] == ' ':
			favorites = 0
		else:
			favorites = float(profile['favourites_count'])

		if profile['followers_count'] == '' or profile['followers_count'] == ' ':
			followers = 0
		else:
			followers = float(profile['followers_count'])

		if profile['friends_count'] == '' or profile['friends_count'] == ' ':
			friends = 0
		else:
			friends = float(profile['friends_count'])

		if profile['listed_count'] == '' or profile['listed_count'] == ' ':
			listed = 0
		else:
			listed = float(profile['listed_count'])

		if profile['created_at'] == '' or profile['created_at'] == ' ':
			creation_time = 0
		else:
			creation_time = get_time(profile['created_at'])

		extra_data = [favorites/float(profile['statuses_count']), followers, friends, listed, creation_time]
		# extra_data.extend(tweet2vec(profile['description']))
		users[key].extend(extra_data)
	# Ignore the tweet otherwise
	else:
		print("Unmatched user: "+str(key))
		to_del.append(key)

for key in to_del:
	del users[key]

to_del = []

for bot, bot_tweets in tqdm(bots.items()):
	extra_data = []
	key = bot.lower()
	if key in bot_user_data:
		missing_data = False
		profile = bot_user_data[key]
		get_time = lambda ts: calendar.timegm(time.strptime(ts,'%a %b %d %H:%M:%S +0000 %Y'))
		if profile['favourites_count'] == '' or profile['favourites_count'] == ' ':
			favorites = 0
			missing_data = True
		else:
			favorites = float(profile['favourites_count'])

		if profile['followers_count'] == '' or profile['followers_count'] == ' ':
			followers = 0
			missing_data = True
		else:
			followers = float(profile['followers_count'])

		if profile['friends_count'] == '' or profile['friends_count'] == ' ':
			friends = 0
			missing_data = True
		else:
			friends = float(profile['friends_count'])

		if profile['listed_count'] == '' or profile['listed_count'] == ' ':
			listed = 0
			missing_data = True
		else:
			listed = float(profile['listed_count'])

		if profile['created_at'] == '' or profile['created_at'] == ' ':
			creation_time = 0
			missing_data = True
		else:
			creation_time = get_time(profile['created_at'])

		if missing_data:
			to_del.append(key)
		else:
			extra_data = [favorites/float(profile['statuses_count']), followers, friends, listed, creation_time]
			# extra_data.extend(tweet2vec(profile['description']))
			bots[key].extend(extra_data)
	# Ignore the tweet otherwise
	else:
		print("Unmatched bot: "+str(key))
		to_del.append(key)

for key in to_del:
	del bots[key]
	

save_obj(users, 'users_features_v4')
save_obj(bots, 'bots_features_v4')
# print("\nUsers:")
# print(users)
# print("\nBots:")
# print(bots)
# print(len(users))
# print(len(bots))

