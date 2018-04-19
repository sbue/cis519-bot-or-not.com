import linecache
import random

num_samples = 50
total_lines = 50000000 * 5 + 1376589

sampled = set()
tweet_ids = set()
for _ in range(num_samples):
	line_number = random.randrange(1, total_lines+1)
	file_number = line_number // 50000000 + 1
	file = 'election-filter{file_number}.txt'
	tweet_id = linecache.getline(file, file_number).strip()
	tweet_ids.add(tweet_id)
