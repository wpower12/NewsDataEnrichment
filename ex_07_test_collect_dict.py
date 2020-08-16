import pymysql
import ArticleNLP.ArticleNLP as anlp
import pickle

import pandas as pd

# Get some articles from the test
# article_f = open('data/NewsArticles.csv', encoding="latin-1")
# articles = pd.read_csv(article_f)

conn = pymysql.connect(user='wpower3', passwd='power12!', host='127.0.0.1', db='news_db_test')
onegrams, twograms, th3grams = anlp.collect_term_dictionary_db(conn, min_percent=0.01, max_percent=0.3)

print(len(onegrams), len(twograms), len(th3grams))

path = "./results/{}"
pickle.dump(onegrams, open(path.format("onegrams_full_test"), "wb"))
pickle.dump(twograms, open(path.format("twograms_full_test"), "wb"))
pickle.dump(th3grams, open(path.format("th3grams_full_test"), "wb"))

