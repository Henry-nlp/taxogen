import subprocess, os
from collections import OrderedDict

from ..tweet_preprocessing.tweet_handler import preprocess_tweet
from ..tweet_preprocessing.tweet_handler import Logger
from ..tweet_preprocessing.paras import load_la_tweets_paras

class LINE:
    def __init__(self, paras):
        self.input = paras['graph_embedding_tweets']
        self.train_nodes = paras['train_nodes']
        self.train_edges = paras['train_edges']
        self.output = paras['embeddings']
        self.size = paras['line_paras']['size']
        self.order = paras['line_paras']['order']
        self.negative = paras['line_paras']['negative']
        self.samples = paras['line_paras']['samples']
        self.rho = paras['line_paras']['rho']
        self.threads = paras['line_paras']['thread']
        self.logger = Logger.get_logger("MAIN LOG")
        self.min_count = paras['line_paras']['min_count']
        self.co_occurrence_tweets = paras['co_occurrence_tweets']

    def build_train_file(self):

        self.logger.info(Logger.build_log_message(self.__class__.__name__, self.build_train_file.__name__,
                                             'Start building training file'))

        with open(self.input, 'r') as f:
            data = f.readlines()

        word_co_occurrence = {}
        word_co_occurrence_tweets = {}

        count = 0

        for tweet in data:
            tweet = preprocess_tweet(tweet, lower=True)
            stweet = tweet.split(' ')

            for i in range(len(stweet)):
                for j in range(i+1, len(stweet)):
                    co_w1 = '{}\t{}'.format(stweet[i], stweet[j])
                    co_w2 = '{}\t{}'.format(stweet[j], stweet[i])
                    co_w = '{}_{}'.format(stweet[i], stweet[j])
                    if co_w1 not in word_co_occurrence:
                        word_co_occurrence[co_w1] = 0
                    if co_w2 not in word_co_occurrence:
                        word_co_occurrence[co_w2] = 0
                    if co_w not in word_co_occurrence_tweets:
                         word_co_occurrence_tweets[co_w] = []

                    word_co_occurrence[co_w1] += 1
                    word_co_occurrence[co_w2] += 1
                    word_co_occurrence_tweets[co_w].append(tweet)

            count += 1

            if count % 10000 == 0:
                self.logger.info(Logger.build_log_message(self.__class__.__name__, self.build_train_file.__name__, '{} lines processed'.format(count)))

        word_co_occurrence = {k: v for k, v in word_co_occurrence.iteritems() if v >= self.min_count}

        res_list = []
        word_set = set()
        for key, val in word_co_occurrence.iteritems():
            res_list.append('{}\t{}\t{}'.format(key, val, 'e'))
            for word in key.split('\t'):
                word_set.add(word)
        with open(self.train_edges, 'wb') as outf:
            outf.write('\n'.join(res_list))
        with open(self.train_nodes, 'wb') as outf:
            outf.write('\n'.join(list(word_set)))

        # count = 0
        # for co_word in word_co_occurrence_tweets:
        #     if len(word_co_occurrence_tweets[co_word]) >= self.min_count:
        #         with open(self.co_occurrence_tweets+co_word+".txt", 'w') as outf:
        #             outf.write('\n'.join(word_co_occurrence_tweets[co_word]))
        #         count += 1
        #         if count % 10000 == 0:
        #             self.logger.info(Logger.build_log_message(self.__class__.__name__, self.build_train_file.__name__, '{} co_occurrence_words processed'.format(count)))

    def run(self):

        if not os.path.exists('word2vec'):
            subprocess.call([''], shell=True)


        return


if __name__ == '__main__':
    git_version = subprocess.Popen('git rev-parse --short HEAD', shell=True, stdout=subprocess.PIPE).communicate()[0].strip('\n')

    paras = load_la_tweets_paras(dir=git_version)
    line = LINE(paras)
    line.build_train_file()

