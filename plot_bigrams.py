import re
import csv
import pickle
import nltk
import collections
import random
import numpy as np
from nltk.tokenize import word_tokenize
from nltk.probability import FreqDist
from nltk.stem import WordNetLemmatizer
from nltk.corpus import stopwords
import matplotlib.pyplot as plt

common_words = set(stopwords.words('english'))
other_ignore = ["'s", "s", "t", "'t"]
wnlemma = WordNetLemmatizer()

def word_plot(text, num_tweets, with_punc=False, bigram=False):
	word_dict = {}
	if (with_punc):
		split_words = word_tokenize(text)
	else:
		split_words = re.split('\W+', text)
	if (bigram):
		bg = list(nltk.bigrams(split_words))
		split_words = []
		for (a, b) in bg:
			a = a.lower()
			b = b.lower()
			if a not in common_words and a not in other_ignore and b not in common_words and b not in other_ignore:
				combined = a+"-"+b
				split_words.append(combined)
	for word in split_words:
		word = wnlemma.lemmatize(word.lower())
		if word not in common_words and word not in other_ignore:
			if word in word_dict.keys():
				word_dict[word] += 1
			else:
				word_dict[word] = 1
	most_common = sorted(word_dict.items(), key=lambda x: -1*x[1])[:30]
	x = np.arange(20)
	fig, ax = plt.subplots()
	unzipped = list(zip(*most_common[:20]))
	freq_vals = []
	for val in unzipped[1]:
		freq_vals.append(val / num_tweets)
	plt.bar(x, freq_vals)
	plt.xticks(x, unzipped[0])
	plt.show()



all_bot_tweets = []
num_bot_tweets = 0
all_ppl_tweets = []
num_ppl_tweets = 0

with open('russian-troll-tweets/tweets.csv', newline='') as csvfile:
	reader = csv.DictReader(csvfile)
	for row in reader:
		all_bot_tweets.append(row)
		num_bot_tweets += 1

with open('election_tweets.csv', newline='') as csvfile:
	reader = csv.DictReader(csvfile)
	for row in reader:
		all_ppl_tweets.append(row)
		num_ppl_tweets += 1

all_bot_tweet_text = ""
all_ppl_tweet_text = ""
for b_tweet in all_bot_tweets:
	all_bot_tweet_text += b_tweet['text']
for p_tweet in all_ppl_tweets:
	all_ppl_tweet_text += p_tweet['text']

word_plot(all_bot_tweet_text, num_bot_tweets, with_punc=False, bigram=False)
# word_plot(all_ppl_tweet_text, num_ppl_tweets, with_punc=False, bigram=False)
# word_plot(all_bot_tweet_text, num_bot_tweets, with_punc=True, bigram=False)
# word_plot(all_ppl_tweet_text, num_ppl_tweets, with_punc=True, bigram=False)
# word_plot(all_bot_tweet_text, num_bot_tweets, with_punc=False, bigram=True)
# word_plot(all_ppl_tweet_text, num_ppl_tweets, with_punc=False, bigram=True)





