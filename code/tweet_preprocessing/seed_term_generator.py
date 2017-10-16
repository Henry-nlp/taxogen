import subprocess, os
from paras import la_pure_tweets, la_pos_tweets, la_keywords, MAIN_LOG, la_category, la_category_keywords, la_embeddings
from datetime import datetime
from util.logger import Logger
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
import json
from tweet_handler import preprocess_tweet

class KeywordGenerator:
    def __init__(self, pure_tweets, pos_tweets, f_out, logger_name, category, category_keywords, embeddings):
        self.pure_tweets = pure_tweets
        self.pos_tweets = pos_tweets
        self.output = f_out
        self.keywords = set()
        self.noun_tag = {'NN', 'NNS', 'NNP', 'NNPS'}
        self.logger = Logger.get_logger(logger_name)
        self.category = category
        self.category_keywords = category_keywords
        self.embeddings = embeddings

    def parse_pos_tweet(self, pos_tweet):
        pos_tweet = preprocess_tweet(pos_tweet, lower=False)
        pos_tweet = pos_tweet.split(' ')

        for segment in pos_tweet:
            segment = segment.strip().split('/')

            if segment[2] in self.noun_tag:
                self.keywords.add(segment[0] + "\n")

    def build_keyword(self):

        self.logger.info(
            Logger.build_log_message(self.__class__.__name__, self.build_keyword.__name__, 'Start building keywords'))

        with open(self.pos_tweets, 'r') as f:
            data = f.readlines()
            count = 0
            for pos_tweet in data:
                self.parse_pos_tweet(pos_tweet)
                count += 1

                if count % 10000 == 0:
                    self.logger.info(Logger.build_log_message(self.__class__.__name__, self.build_keyword.__name__,
                                                              '%s pos tag tweets processed' % count))

        self.logger.info(
            Logger.build_log_message(self.__class__.__name__, self.build_keyword.__name__, 'Write keywords to file'))

        with open(self.output, 'w+') as f:
            f.writelines(self.keywords)

        self.logger.info(
            Logger.build_log_message(self.__class__.__name__, self.build_keyword.__name__, 'Finish building keywords'))

    def build_pos_tag_tweets(self):

        self.logger.info(Logger.build_log_message(self.__class__.__name__, self.build_pos_tag_tweets.__name__,
                                                  'Start building pos tag tweets'))
        p = subprocess.Popen('shell_script/pos_tag.sh %s %s' % (self.pure_tweets, self.pos_tweets), shell=True)
        p.communicate()
        self.logger.info(Logger.build_log_message(self.__class__.__name__, self.build_pos_tag_tweets.__name__,
                                                  'Finish building pos tag tweets'))

    def build_category_keywords(self):
        with open(self.category, 'r') as f:
            data = f.read()
        category_dict = json.loads(data)
        category_dict = category_dict['categories']
        category_keywords = self.recursive_build_category_keywords(category_dict)

        with open(self.category_keywords, 'w+') as fout:
            fout.write(' '.join(category_keywords))

    def recursive_build_category_keywords(self, category_dict):
        if len(category_dict) == 0:
            return []

        keywords = []
        for category in category_dict:
            name = preprocess_tweet(category['name']).encode('ascii', 'ignore')
            words = name.split()
            words = [word for word in words if len(word) > 1]
            keywords.extend(words)
            child_keywords = self.recursive_build_category_keywords(category['categories'])
            keywords.extend(child_keywords)
        return keywords

    def match_category_keyword(self):

        with open(self.embeddings, 'r') as f:
            embedding_data = f.readlines()
        with open(self.category_keywords, 'r') as f:
            category_keywords = preprocess_tweet(f.read()).split(' ')
        with open(self.output, 'r') as f:
            keywords = f.readlines()

        embed_dic = {}
        dim_len = int(embedding_data[0].strip().strip('\n').split(' ')[-1])
        # print dim_len
        # skip the first line since its metadata(number of words, embedding dim)
        for line in embedding_data[1:]:
            line = preprocess_tweet(line, lower=False)
            line = line.split(' ')
            embed_dic[line[0].strip()] = np.asarray([float(i) for i in line[1:]]).reshape((1, dim_len))

        category_keywords_dic = {}
        cosine_cate = {}
        for word in category_keywords:
            word = word.lower()
            if word in embed_dic:
                category_keywords_dic[word] = embed_dic[word]
                cosine_cate[word] = []

        # print category_keywords_dic.keys()
        # print embed_dic.keys()
        count = 0
        for word in keywords:
            word = preprocess_tweet(word)
            word = word.strip().strip('\n').lower()
            count += 1
            if word in embed_dic:
                # print word
                word_embed = embed_dic[word]
                for cate in category_keywords_dic:
                    # print cosine_similarity(word_embed, category_keywords_dic[cate])
                    cossim = cosine_similarity(word_embed, category_keywords_dic[cate])[0][0]
                    if cossim >= 0.5:
                        cosine_cate[cate].append(word)
                        break

            if count % 10000 == 0:
                print "%s keywords processed" % count
        with open('test.txt', 'w+') as fout:
            json.dump(cosine_cate, fout, indent=4)



if __name__ == '__main__':
    start = datetime.utcnow()
    gen = KeywordGenerator(la_pure_tweets, la_pos_tweets, la_keywords, MAIN_LOG, la_category, la_category_keywords, la_embeddings)
    # gen.build_pos_tag_tweets()
    # gen.build_keyword()
    gen.build_category_keywords()
    gen.match_category_keyword()
    finish = datetime.utcnow()
    exec_time = finish - start
    print exec_time.seconds
    print exec_time.microseconds
