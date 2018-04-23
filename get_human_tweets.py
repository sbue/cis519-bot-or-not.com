import os
import linecache
import random
import twitter
from tqdm import tqdm
from time import sleep
from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv())

num_samples = 50
total_lines = 50000000 * 5 + 1376589
sampled_lines = {i: [] for i in range(1, 7)}
for _ in range(num_samples):
    line_number = random.randrange(1, total_lines+1)
    file_number = line_number // 50000000 + 1
    line_number = line_number - (50000000 * (file_number-1))
    sampled_lines[file_number].append(line_number)

sampled_lines = {i: sorted(sampled_lines[i]) for i in sampled_lines}
tweet_ids = set()
for i in tqdm(range(1, 7)):
    with open(f'election-filter{i}.txt', 'r') as f:
        lines = f.readlines()
        for l in sampled_lines[i]:
            tweet_ids.add(lines[l-1].strip())

tweet_ids_list = list(tweet_ids)
tweets = []
for tweet_id in tweet_ids:
    try:
        twitter_api = twitter.Api(consumer_key=os.getenv('CONSUMER_KEY'),
                          consumer_secret=os.getenv('CONSUMER_SECRET'),
                          access_token_key=os.getenv('ACCESS_TOKEN_KEY'),
                          access_token_secret=os.getenv('ACCESS_TOKEN_SECRET'))
        tweets.append(twitter_api.GetStatus(tweet_id))
        sleep(0.3)
    except twitter.error.TwitterError:
        pass

