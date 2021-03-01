import tweet_generator 

tweets = tweet_generator.lastweek_stats()

for i in tweets:
    print(i, "\n\t", len(i), "\n")