from scipy.sparse import coo_matrix
import pandas as pd, numpy as np
import pickle
import dill
from hpfrec import HPF

K = 15
top_N = 5

path = "./results"
term_map, term_dict, artid_map, article_counts = pickle.load(open("{}/article_summary_full_test".format(path), "rb"))

topic_model = HPF(k=K)
topic_model.fit(coo_matrix(np.asarray(article_counts)))

dill.dump(topic_model, open("{}/test_HPF_topic_model".format(path), 'wb'))

