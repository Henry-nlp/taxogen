import subprocess
from util.logger import Logger
from tweet_handler import TweetHandler
from paras import la_log, la_tweets, la_input, la_pos_tweets, la_keywords, la_pure_tweets, lexnorm, MAIN_LOG
from seed_term_generator import KeywordGenerator


if __name__ == '__main__':
    git_version = subprocess.Popen('git rev-parse --short HEAD', shell=True, stdout=subprocess.PIPE).communicate()[0]
    logger = Logger(la_log+git_version.strip()+"/log.txt")

    # generate lexnorm.txt and pure_tweets.txt
    tweet_handler = TweetHandler(la_tweets, la_input, MAIN_LOG, lexnorm)
    tweet_handler.preprocess()

    # generate pos_tag_tweets.txt and keywords.txt
    gen = KeywordGenerator(la_pure_tweets, la_pos_tweets, la_keywords, MAIN_LOG)
    gen.build_pos_tag_tweets()
    gen.build_keyword()
