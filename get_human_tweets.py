import os
import linecache
import random
import twitter
from tqdm import tqdm
from time import sleep
from datetime import datetime
from dotenv import load_dotenv, find_dotenv
import boto3

ec2 = boto3.client('ec2', region_name='us-east-1b')

load_dotenv(find_dotenv())

TOTAL_LINES = 50000000 * 5 + 1376589
SAMPLE_BATCH_SIZE = 1000

sampled = set()
users = set()

sampled_lines = {i: [] for i in range(1, 7)}
for _ in range(SAMPLE_BATCH_SIZE):
    line_number = random.randrange(1, TOTAL_LINES + 1)
    while line_number in sampled:
        line_number = random.randrange(1, TOTAL_LINES + 1)
    file_number = line_number // 50000000 + 1
    line_number = line_number - (50000000 * (file_number - 1))
    sampled_lines[file_number].append(line_number)

sampled_lines = {i: sorted(sampled_lines[i]) for i in sampled_lines}
tweet_ids = set()
for i in tqdm(range(1, 7)):
    with open(f'election-filter{i}.txt', 'r') as f:
        lines = f.readlines()
        for l in sampled_lines[i]:
            tweet_ids.add(lines[l-1].strip())

tweet_ids_list = list(tweet_ids)
user_tweets = {}
for tweet_id in tweet_ids:
    try:
        twitter_api = twitter.Api(consumer_key=os.getenv('TW_CONSUMER_KEY'),
                          consumer_secret=os.getenv('TW_CONSUMER_SECRET'),
                          access_token_key=os.getenv('TW_ACCESS_TOKEN_KEY'),
                          access_token_secret=os.getenv('TW_ACCESS_TOKEN_SECRET'))
        tweet = twitter_api.GetStatus(tweet_id)
        user_id = tweet.user.id
        if user_id in users:
            continue
        user_timeline_all = []
        user_timeline = twitter_api.GetTimeline(user_id, count=200)
        while len(user_timeline) == 200:
            user_timeline_all.extend(user_timeline)
            oldest = user_timeline_all[-1].id - 1
            user_timeline = twitter_api.GetTimeline(user_id, count=200, max_id=oldest)
            print(f'...{len(user_timeline_all)} tweets downloaded so far')
        user_tweets[user_id] = user_timeline_all
        datetime_object = datetime.strptime('Jun 1 2005  1:33PM', '%b %d %Y %I:%M%p')
        sleep(0.1)
    except twitter.error.TwitterError:
        pass
