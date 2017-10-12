import subprocess
import logging
from util.logger import Logger
from tweet_handler import TweetHandler
from paras import la_log, la_tweets, la_input, la_pos_tweets, la_keywords, la_pure_tweets, lexnorm
from seed_term_generator import KeywordGenerator





if __name__ == '__main__':
    logger = Logger(la_log)

    # generate lexnorm.txt and pure_tweets.txt
    tweet_handler = TweetHandler(la_tweets, la_input, la_log, lexnorm)
    tweet_handler.preprocess()

    #generate pos_tag_tweets.txt and keywords.txt
    gen = KeywordGenerator(la_pure_tweets, la_pos_tweets, la_keywords)
    gen.build_keyword()
