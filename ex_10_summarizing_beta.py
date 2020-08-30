from scipy.sparse import coo_matrix
import pandas as pd, numpy as np
import pickle
import dill
from hpfrec import HPF

K = 10
top_N = 15
path = "./results"

term_map, term_dict, artid_map, article_counts = pickle.load(open("{}/article_summary_full_test".format(path), "rb"))
topic_model = dill.load(open("{}/test_HPF_topic_model".format(path), 'rb'))

term_keys = list(term_map.keys())
term_vals = list(term_map.values())

for k in topic_model.Beta.T:
    top_N_idxs = np.argpartition(k, -1*top_N)[-1*top_N:]
    terms = [term_keys[term_vals.index(i)] for i in top_N_idxs]
    print(terms)

print(topic_model.Beta.shape)

