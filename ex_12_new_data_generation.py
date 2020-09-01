import ArticleNLP.ArticleNLP as anlp
import pymysql
import numpy as np
import pandas as pd
from scipy import sparse
from sklearn.feature_extraction.text import CountVectorizer

SAVE_PATH = "results/test_dataset_gen"

conn = pymysql.connect(user='wpower3', passwd='power12!', host='127.0.0.1', db='news_db_test')
article_data_full = anlp.get_full_dataset(conn, testing=True)

###  Data Frames
# Full Data Frame from db
cols = ["article_id", "article_text", "news_outlet"]
article_df = pd.DataFrame(data=article_data_full, columns=cols)

#Getting Outlet list and counts
outlets = article_df["news_outlet"]
outlet_list, outlet_counts = np.unique(outlets, return_counts=True)

# Creating 'author maps' - 'outlet map'
outlet_to_outletid = dict([(y.title(), x) for x,y in enumerate(sorted(set(outlet_list)))])

# List of outlet_ids indexed on the same index as the article data.
## SRC: author_indices.npy
outlet_ids = np.array([outlet_to_outletid[o.title()] for o in outlets])
np.save("{}/author_indices.npy".format(SAVE_PATH), outlet_ids)

# This also gets us our author_map for the data we need.
## SRC: author_map.txt
author_map = np.array(list(outlet_to_outletid.keys()))
np.savetxt("{}/author_map.txt".format(SAVE_PATH), author_map, fmt="%s")
print("Saved author indices and map.")

### Processing the Text/Getting Gram counts
# Load the stop words - Using their set for the senate data.
stopwords = set(np.loadtxt("data/stops_senate_speeches.txt", dtype=str, delimiter="\n"))
count_vectorizer = CountVectorizer(min_df=0.001,
                                   max_df=0.3,
                                   stop_words=stopwords,
                                   ngram_range=(1, 3),
                                   token_pattern="[a-zA-Z]+")

article_text = article_df["article_text"]
counts = count_vectorizer.fit_transform(article_text)
## SRC: vocabulary.txt
vocabulary = np.array([k for (k, v) in sorted(count_vectorizer.vocabulary_.items(),
                                              key=lambda kv: kv[1])])
np.savetxt("{}/vocabulary.txt".format(SAVE_PATH), vocabulary, fmt="%s")
print("Saved vocabulary.txt")

# Get dense counts? Not sure what this does. Need to read. Also, borrowing their code here. ## ATTRIBUTION NEEDED ##
## SRC: counts.npz
counts_dense = anlp.remove_cooccurring_ngrams(counts, vocabulary)
sparse.save_npz("{}/counts.npz".format(SAVE_PATH), sparse.csr_matrix(counts_dense).astype(np.float32))
print("saved counts.")

