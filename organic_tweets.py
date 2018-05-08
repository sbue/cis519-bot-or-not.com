import os
import linecache
import random
import twitter
import time
import pickle
import gc
import boto3
import time
import pandas as pd
from tqdm import tqdm
from datetime import datetime
from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv())

# Globals
SAMPLE_SIZE = 100000

# Date / Time Utils
fmt = '%Y-%m-%d %H:%M:%S'
START_TIMESTAMP = time.strptime("2014-07-14 18:04:55", fmt)
END_TIMESTAMP = time.strptime("2017-09-26 09:05:32", fmt)
in_range = lambda ts: ts >= START_TIMESTAMP and ts <= END_TIMESTAMP
to_iso = lambda ts: time.strptime(ts,'%a %b %d %H:%M:%S +0000 %Y')
to_str = lambda ts: time.strftime('%Y-%m-%d %H:%M:%S', ts)

# Get a set of tweet ids
def get_tweet_id_samples(sample_size=SAMPLE_SIZE):
    try:
        tweet_ids = pickle.load(open(f'data/tweet_ids', "rb"))
    # If tweets, not picked, create pickle
    except (OSError, IOError) as e:
        TOTAL_LINES = 251376589
        sampled, sampled_lines = set(), {i: [] for i in range(1, 7)}
        # Get a sample of file lines associated with tweet ids data
        for _ in range(sample_size):
            line_number = random.randrange(1, TOTAL_LINES + 1)
            while line_number in sampled:
                line_number = random.randrange(1, TOTAL_LINES + 1)
            sampled.add(line_number)
            file_number = line_number // 50000000 + 1
            line_number = line_number - (50000000 * (file_number - 1))
            sampled_lines[file_number].append(line_number)
        sampled_lines = {i: sorted(sampled_lines[i]) for i in sampled_lines}
        tweet_ids = set()
        # Get tweet ids from file lines
        for i in tqdm(range(1, 7)):
            f = open(f'data/election-filter{i}.txt', 'r')
            lines = f.readlines()
            for l in sampled_lines[i]:
                tweet_ids.add(lines[l-1].strip())
            f.close()
            del lines
            del f
            gc.collect()
        pickle.dump(tweet_ids, open(f'data/tweet_ids', "wb"))
    return tweet_ids

tweet_ids = get_tweet_id_samples()
twitter_api = twitter.Api(consumer_key=os.getenv('TW_CONSUMER_KEY'),
                  consumer_secret=os.getenv('TW_CONSUMER_SECRET'),
                  access_token_key=os.getenv('TW_ACCESS_TOKEN_KEY'),
                  access_token_secret=os.getenv('TW_ACCESS_TOKEN_SECRET'), 
                  sleep_on_rate_limit=True)

def get_user_id(tweet_id):
    try:
        # get user from tweet
        tweet = twitter_api.GetStatus(tweet_id)
        user_id = tweet.user.id
        return user_id
    except twitter.error.TwitterError:
        pass

def get_tweets_data(user_id):
    try:
        # exhaust twitter api for full user timeline
        user_timeline = []
        tl = twitter_api.GetUserTimeline(user_id, count=200)
        user_timeline.extend(tl)
        while len(tl) > 0:
            oldest = user_timeline[-1].id - 1
            tl = twitter_api.GetUserTimeline(user_id, count=200, max_id=oldest)
            user_timeline.extend(tl)
        
        # filter user timeline
        user_timeline = [tw for tw in user_timeline if 
                         in_range(to_iso(tw.created_at))]
        return user_timeline
    except twitter.error.TwitterError:
        pass

def get_user_data(user_id):
    try:
        u = twitter_api.GetUser(user_id)
        return u
    except twitter.error.TwitterError as e:
        pass

# dynamodb = boto3.resource('dynamodb', region_name='us-east-1', 
#                         aws_access_key_id=os.getenv('AWS_ACCESS_KEY'), 
#                         aws_secret_access_key=os.getenv('AWS_SECRET_KEY'))
# tweets_tb = dynamodb.Table('election_tweets_tb')

tweets_df = pd.read_csv('data/organic_tweets.csv') # pd.DataFrame(data=users_data)
users_df = pd.read_csv('data/organic_users.csv') # pd.DataFrame(data=users_data)
users = set(users_df['id'].unique())

CAP = 2000

users_data = []
tweets_data = []

def data_to_csv():
    last_user = users_data[-1]
    users_new = pd.DataFrame(data=users_data[:-1])
    tweets_new = pd.DataFrame(data=tweets_data)
    users_new['id'] = users_new['id'].astype(str)
    tweets_new['user_id'] = tweets_new['user_id'].astype(str)
    tweets_new['tweet_id'] = tweets_new['tweet_id'].astype(str)
    tweets_new = tweets_new[tweets_new['user_id'] != str(last_user)]
    t = pd.concat([tweets_df, tweets_new], ignore_index=True)
    u = pd.concat([users_df, users_new], ignore_index=True)
    t.to_csv('data/organic_tweets.csv', index=False)
    u.to_csv('data/organic_users.csv', index=False)

try:
    for tweet_id in tqdm(list(tweet_ids)[1500:CAP]):
        user_id = get_user_id(tweet_id)
        if user_id in users:
            continue
        users.add(user_id)
        u = get_user_data(user_id)
        if not u:
            continue
        u_tweets_data = get_tweets_data(user_id) 
        if not u_tweets_data or len(u_tweets_data) == 0:
            continue
        user = {
            'id': str(u.id),
            'location': u.location,
            'name': u.name,
            'followers_count': u.followers_count,
            'statuses_count': u.statuses_count,
            'time_zone': u.time_zone,
            'verified': u.verified,
            'lang': u.lang,
            'screen_name': u.screen_name,
            'description': u.description,
            'created_at': u.created_at,
            'favourites_count': u.favourites_count,
            'friends_count': u.friends_count,
            'listed_count': u.listed_count
        }
        users_data.append(user)
        # for every tweet a user has sent
        for t in u_tweets_data:
            # write tweet to dynamodb database
            tweet = {
                    'tweet_id': str(t.id),
                    'user_id': str(t.user.id),
                    'user_key': t.user.screen_name,
                    'created_at': None,
                    'created_str': to_str(to_iso(t.created_at)),
                    'retweet_count': t.retweet_count,
                    'retweeted': t.retweeted,
                    'favorite_count': t.favorite_count,
                    'text': t.text,
                    'hashtags': str([h.text for h in t.hashtags]),
                    'mentions': str([u.screen_name for u in t.user_mentions]),
                    'in_reply_to_status_id': str(t.in_reply_to_status_id)
                }
            tweets_data.append(tweet)

except KeyboardInterrupt:
    data_to_csv()
    exit()

data_to_csv()
