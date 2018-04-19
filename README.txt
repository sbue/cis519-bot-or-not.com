This dataset contains the tweet ids of approximately 280 million tweets related
to the 2016 United States presidential election.  They were collected between
July 13, 2016 and November 10, 2016 from the Twitter API using Social Feed
Manager (http://gwu-libraries.github.io/sfm-ui/).


These tweet ids are broken up into 12 collections.  Each collection was
collected either from the GET statuses/user_timeline method of the Twitter REST
API (https://dev.twitter.com/rest/reference/get/statuses/user_timeline) or the
POST statuses/filter method of the Twitter Stream API
(https://dev.twitter.com/streaming/reference/post/statuses/filter).  The
collections are:
* Candidates and key election hashtags (Twitter filter): election-filter[1-6].txt
* Democratic candidates (Twitter user timeline): democratic-candidate-timelines.txt
* Democratic Convention (Twitter filter): democratic-convention-filter.txt
* Democratic Party (Twitter user timeline): democratic-party-timelines.txt
* Election Day (Twitter filter): election-day.txt
* First presidential debate (Twitter filter): first-debate.txt
* GOP Convention (Twitter filter): republican-convention-filter.txt
* Republican candidates (Twitter user timeline): republican-candidate-timelines.txt
* Republican Party (Twitter user timeline): republican-party-timelines.txt
* Second presidential debate (Twitter filter): second-debate.txt
* Third presidential debate (Twitter filter): third-debate.txt
* Vice Presidential debate (Twitter filter): vp-debate.txt

There is also a README.txt file for each collection containing additional documentation on 
how it was collected.

The GET statuses/lookup method (https://dev.twitter.com/rest/reference/get/statuses/lookup)
supports retrieving the complete tweet for a tweet id (known as hydrating).
Tools such as Twarc (https://github.com/DocNow/twarc) or Hydrator
(https://github.com/DocNow/hydrator) can be used to hydrate tweets.  When
hydrating be aware that:
* Twitter limits hydration to 900 requests of 100 tweet ids per 15 minute window
  per set of user credentials.  This works out to 8,640,000 tweets per day, so
  hydrating this entire dataset will take 32 days.
* The Twitter API will not return tweets that have been deleted or belong to
  accounts that have been suspended, deleted, or made private. You should expect
  a large number of these tweets to be unavailable.

There may be duplicate tweets across collections.  Also, according to the
Twitter documentation, duplicates tweets are possible for tweets collected from
the Twitter filter stream.

For tweets collected from the Twitter filter stream, this is not a complete set
of tweets that match the filter.  Gaps may exist because:
* Twitter limits the number of tweets returned by the filter at any point in time.
* Social Feed Manager stops and starts the Twitter filter stream every 30 minutes.
* In Social Feed Manager, collecting is turned off while a user is making changes
  to the collection criteria.
* There were some operational issues, e.g., network interruptions, during the
  collection period.

Since some of the terms used to collect from the Twitter filter stream were
broad (e.g., “election”), it may contain tweets from elections other than the
U.S. presidential election, including state elections, local elections, or
elections in other countries.

Per Twitter’s Developer Policy (https://dev.twitter.com/overview/terms/policy.html#id8),
tweet ids may be publicly shared; tweets may not.

Questions about this dataset can be sent to sfm@gwu.edu.  George Washington
University researchers should contact us for access to the tweets.


This work is supported by grant #NARDI-14-50017-14 from the National Historical
Publications and Records Commission.
