import pymysql
import ArticleNLP.ArticleNLP as anlp
import pickle
import numpy as np

path = "./results"
gram_fns = ["onegrams_full_test", "twograms_full_test", "th3grams_full_test"]
grams = [pickle.load(open("{}/{}".format(path, i), "rb")) for i in gram_fns]

term_map, term_dict = anlp.make_term_dict(grams)

conn = pymysql.connect(user='wpower3', passwd='power12!', host='127.0.0.1', db='news_db_test')
article_counts, artid_map  = anlp.get_article_term_counts(conn, term_map)
article_counts = np.asarray(article_counts)

# should return a N_articles x N_terms matrix.
print(artid_map)
print(article_counts.shape)

summary_obj = [term_map, term_dict, artid_map, article_counts]
pickle.dump(summary_obj, open("{}/article_summary_full_test".format(path), "wb"))
