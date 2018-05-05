import re
import csv
import pickle
import nltk
import collections
import random
import numpy as np
from nltk.stem import WordNetLemmatizer
from nltk.corpus import stopwords

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
bots = {}
users = {}

final_embeddings = load_obj('final_embeddings')
reverse_dict = load_obj('reverse_dictionary')
word2vec_dict = load_obj('word2vec_dictionary')

# Extract all tweets from the csv file
with open('russian-troll-tweets/tweets.csv', newline='') as csvfile:
	reader = csv.DictReader(csvfile)
	for row in reader:
		all_bot_tweets.append(row)

with open('election_tweets.csv', newline='') as csvfile:
	reader = csv.DictReader(csvfile)
	for row in reader:
		all_ppl_tweets.append(row)
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
all_tweet_text = ""
for tweet in all_bot_tweets:
	all_tweet_text += tweet['text']
for tweet in all_bot_tweets:
	all_tweet_text += tweet['text']
# TODO: tweets_word2vec with full tweet text body data

# Takes a tweet text and converts it to a more meaningful feature vector 
# for input to the learning algorithm
def process_tweet(text):
	index = 0
	retweet = 0
	num_other_at = 0
	num_hashtags = 0
	avg_hashtag = None
	num_links = 0
	num_words = 0
	avg_word = None
	if text[0:2] == "RT":
		retweet = 1
		index = 4
		while text[index] != ' ':
			index += 1
			if index >= len(text):
				feature = [1, 0, 0]
				feature.extend(final_embeddings[0])
				feature.extend([0, 0])
				feature.extend(final_embeddings[0])
				return feature;
		rt_at = text[4:index]
	text = text[index:]
	pieces = text.split(' ,;"()')
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
	# print("Hashtags:")
	# print(avg_hashtag)
	# print("Words:")
	# print(avg_word)
	feature = [retweet, num_other_at, num_hashtags]
	feature.extend(avg_hashtag)
	feature.extend([num_links, num_words])
	feature.extend(avg_word)
	# feature = [retweet, num_other_at, num_hashtags] + avg_hashtag + [num_links, num_words] + avg_word
	return feature


def avg_tweets(tweets):
	unk_token = final_embeddings[0]
	if len(tweets) == 0:
		return [0, 0, 0] + unk_token + [0, 0] + unk_token
	running_avg = tweets[0]
	num_tweets = 1
	if len(tweets) == 1:
		return running_avg
	for tweet in tweets[1:]:
		index = 0
		while index < len(tweet):
			running_avg[index] += tweet[index]
			index += 1
		num_tweets += 1
	index = 0
	while index < len(running_avg):
		running_avg[index] /= num_tweets
		index += 1
	return running_avg
	

# Extract all users from csv file
with open('russian-troll-tweets/users.csv', newline='') as csvfile:
	reader = csv.DictReader(csvfile)
	for row in reader:
		non_id_keys = list(row.keys())
		non_id_keys.remove('id')
		# TODO: uncomment this line once organic user data is obtained
		# bots[row['id']] = {k: row[k] for k in non_id_keys}
		bots[row['id']] = [] # TODO: include user data in addition to tweets, so change this into a dictionary?

for tweet in all_ppl_tweets:
	# TODO: use other user data
	if tweet['user_id'] in users:
		tweet_text = process_tweet(tweet['text'])
		users[tweet['user_id']].append(tweet_text)
	else:
		tweet_text = process_tweet(tweet['text'])
		users[tweet['user_id']] = [tweet_text]

# Add all extracted and processed tweets to their corresponding user
for tweet in all_bot_tweets:
	# TODO: use other user data
	if tweet['user_id'] in bots:
		tweet_text = process_tweet(tweet['text'])
		bots[tweet['user_id']].append(tweet_text)
	else:
		print("Unmatched tweet: "+str(tweet))
		tweet_text = process_tweet(tweet['text'])
		bots[tweet['user_id']] = [tweet_text]

x = True
for user, user_tweets in users.items():
	if x:
		print(user_tweets)
	avg_user_tweets = avg_tweets(user_tweets)
	users[user] = avg_user_tweets
	if x:
		print(avg_user_tweets)
		x = False

for bot, bot_tweets in bots.items():
	avg_bot_tweets = avg_tweets(bot_tweets)
	bots[bot] = avg_bot_tweets

save_obj(users, 'users_features')
save_obj(bots, 'bots_features')



