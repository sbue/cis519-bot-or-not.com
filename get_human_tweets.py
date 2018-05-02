import os
import linecache
import random
import twitter
import time
import pickle
import gc
import boto3
from tqdm import tqdm
from time import sleep
from datetime import datetime
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())
fmt = '%Y-%m-%d %H:%M:%S'
START_TIMESTAMP = time.strptime("2014-07-14 18:04:55", fmt)
END_TIMESTAMP = time.strptime("2017-09-26 09:05:32", fmt)

users = set()
sampled = set()

try:
    tweet_ids = pickle.load(open(f'tweet_ids', "rb"))
except (OSError, IOError) as e:
    TOTAL_LINES = 50000000 * 5 + 1376589
    SAMPLE_BATCH_SIZE = 100000

    sampled_lines = {i: [] for i in range(1, 7)}
    for _ in range(SAMPLE_BATCH_SIZE):
        line_number = random.randrange(1, TOTAL_LINES + 1)
        while line_number in sampled:
            line_number = random.randrange(1, TOTAL_LINES + 1)
        sampled.add(lined_number)
        file_number = line_number // 50000000 + 1
        line_number = line_number - (50000000 * (file_number - 1))
        sampled_lines[file_number].append(line_number)
    sampled_lines = {i: sorted(sampled_lines[i]) for i in sampled_lines}
    tweet_ids = set()
    for i in tqdm(range(1, 7)):
        f = open(f'election-filter{i}.txt', 'r')
        lines = f.readlines()
        for l in sampled_lines[i]:
            tweet_ids.add(lines[l-1].strip())
        del lines
        f.close()
        del f
        gc.collect()
    pickle.dump(tweet_ids, open(f'tweet_ids', "wb"))

dynamodb = boto3.resource('dynamodb', region_name='us-east-1', 
                        aws_access_key_id=os.getenv('AWS_ACCESS_KEY'), 
                        aws_secret_access_key=os.getenv('AWS_SECRET_KEY'))
tweets_tb = dynamodb.Table('election_tweets_tb')
twitter_api = twitter.Api(consumer_key=os.getenv('TW_CONSUMER_KEY'),
                  consumer_secret=os.getenv('TW_CONSUMER_SECRET'),
                  access_token_key=os.getenv('TW_ACCESS_TOKEN_KEY'),
                  access_token_secret=os.getenv('TW_ACCESS_TOKEN_SECRET'))
to_iso = lambda ts: time.strptime(ts,'%a %b %d %H:%M:%S +0000 %Y')
to_str = lambda ts: time.strftime('%Y-%m-%d %H:%M:%S', ts)
in_range = lambda ts: ts >= START_TIMESTAMP and ts <= END_TIMESTAMP
for tweet_id in tweet_ids:
    try:
        tweet = twitter_api.GetStatus(tweet_id)
        user_id = tweet.user.id
        if user_id in users:
            continue
        users.add(user_id)
        user_timeline = []
        tl = twitter_api.GetUserTimeline(user_id, count=200)
        user_timeline.extend(tl)
        while len(tl) > 0:
            oldest = user_timeline[-1].id - 1
            tl = twitter_api.GetUserTimeline(user_id, count=200, max_id=oldest)
            user_timeline.extend(tl)
        all_tweets = len(user_timeline) < 3200
        before_count = len(user_timeline)
        user_timeline = [tw for tw in user_timeline if in_range(to_iso(tw.created_at))]
        after_count = len(user_timeline)
        print(f'\t{before_count} tweets downloaded, {after_count} preserved')

        if len(user_timeline) == 0:
            continue
        for t in user_timeline:
            response = tweets_tb.put_item(
                Item = {
                    'tweet_id': str(t.id),
                    'user_id': t.user.id,
                    'user_key': t.user.screen_name,
                    'created_at': None,
                    'created_str': to_str(to_iso(t.created_at)),
                    'retweet_count': t.retweet_count,
                    'retweeted': t.retweeted,
                    'favorite_count': t.favorite_count,
                    'text': t.text,
                    'hashtags': str([h.text for h in t.hashtags]),
                    'mentions': str([u.screen_name for u in t.user_mentions]),
                    'in_reply_to_status_id': t.in_reply_to_status_id
                }
            )
            print(response['ResponseMetadata']['HTTPStatusCode'])
    except twitter.error.TwitterError:
        pass
