import subprocess, os
from util.logger import Logger
from tweet_handler import TweetHandler
import paras
from seed_term_generator import SeedTermGenerator

if __name__ == '__main__':
    git_version = subprocess.Popen('git rev-parse --short HEAD', shell=True, stdout=subprocess.PIPE).communicate()[0]
    la_paras = paras.load_la_tweets_paras()

    dir = la_paras['log'] + git_version.strip('\n')
    if not os.path.exists(dir):
        os.mkdir(dir)

    logger = Logger(dir + "/log.txt")
    # generate lexnorm.txt, pure_tweets.txt, embeddings.txt
    tweet_handler = TweetHandler(la_paras, paras.MAIN_LOG, paras.lexnorm)
    #tweet_handler.preprocess()
    tweet_handler.build_hashtags()
    # generate pos_tag_tweets.txt and keywords.txt
    #gen = SeedTermGenerator(paras, paras.MAIN_LOG)
    #gen.build_pos_tag_tweets()
    #gen.build_keyword()
