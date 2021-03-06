import nltk
from nltk.lm import NgramCounter
import numpy as np
from scipy.sparse import *

def collect_ngrams(articles):
    onegram_counts = dict()
    twogram_counts = dict()
    th3gram_counts = dict()

    for index, row in articles.iterrows():
        # We update the counts so they reflect the number of articles each 1,2, and 3 gram shows up in
        try:
            text_tokens = clean_and_split_text(row['text'])
            art_ngrams = NgramCounter([nltk.ngrams(text_tokens, 1),
                                       nltk.ngrams(text_tokens, 2),
                                       nltk.ngrams(text_tokens, 3)])

            # 1 Grams.
            for gram in art_ngrams[1].items():
                gram_str = gram[0]
                if gram_str not in onegram_counts:
                    onegram_counts[gram_str] = 1
                else:
                    onegram_counts[gram_str] += 1

            # 2 Grams
            for gram in art_ngrams[2].items():
                # This iterator returns a 'set'/freqdist for each first word of all its second words.
                for term2 in gram[1]:  # This iterates over all the non-0 prob samples (all second words)
                    gram_str = gram[0][0] + "," + term2
                    if gram_str not in twogram_counts:
                        twogram_counts[gram_str] = 1
                    else:
                        twogram_counts[gram_str] += 1

            # 3 Grams
            for gram in art_ngrams[3].items():
                # This iterator returns a pair of words, and then a freqdist for the 3rd word.
                for term3 in gram[1]:
                    gram_str = gram[0][0] + "," + gram[0][1] + "," + term3
                    if gram_str not in th3gram_counts:
                        th3gram_counts[gram_str] = 1
                    else:
                        th3gram_counts[gram_str] += 1

        except AttributeError:
            # Not sure why/how these are cropping up.
            pass

    return onegram_counts, twogram_counts, th3gram_counts


def collect_term_dictionary(articles, min_percent=0.001, max_percent=0.30):
    print("collecting ngrams.")
    onegrams, twograms, th3grams = collect_ngrams(articles)

    # Need to find the threshold count values for keeping one of the grams
    min_count = max(int(min_percent*len(articles)), 10)
    max_count = int(max_percent*len(articles))
    print("filtering ngrams: max_count {}, min_count {}.".format(max_count, min_count))

    onegrams = dict(filter(lambda e: (e[1] > min_count) and (e[1] < max_count), onegrams.items()))
    twograms = dict(filter(lambda e: (e[1] > min_count) and (e[1] < max_count), twograms.items()))
    th3grams = dict(filter(lambda e: (e[1] > min_count) and (e[1] < max_count), th3grams.items()))

    return onegrams, twograms, th3grams


def collect_ngrams_db(conn, testing=False):
    cur = conn.cursor()

    if testing:
        sql = "SELECT * FROM news_db_test.article_text LIMIT 100;"
    else:
        sql = "SELECT * FROM news_db_test.article_text;"

    cur.execute(sql)
    count = 0
    onegram_counts = dict()
    twogram_counts = dict()
    th3gram_counts = dict()
    article = cur.fetchone()
    while article:
        # We update the counts so they reflect the number of articles each 1,2, and 3 gram shows up in
        try:
            text = clean_and_split_text(article[1])
            art_ngrams = NgramCounter([nltk.ngrams(text, 1), nltk.ngrams(text, 2), nltk.ngrams(text, 3)])

            # 1 Grams.
            for gram in art_ngrams[1].items():
                gram_str = gram[0]
                if gram_str not in onegram_counts:
                    onegram_counts[gram_str] = 1
                else:
                    onegram_counts[gram_str] += 1

            # 2 Grams
            for gram in art_ngrams[2].items():
                # This iterator returns a 'set'/freqdist for each first word of all its second words.
                for term2 in gram[1]:  # This iterates over all the non-0 prob samples (all second words)
                    gram_str = gram[0][0] + "," + term2
                    if gram_str not in twogram_counts:
                        twogram_counts[gram_str] = 1
                    else:
                        twogram_counts[gram_str] += 1

            # 3 Grams
            for gram in art_ngrams[3].items():
                # This iterator returns a pair of words, and then a freqdist for the 3rd word.
                for term3 in gram[1]:
                    gram_str = gram[0][0] + "," + gram[0][1] + "," + term3
                    if gram_str not in th3gram_counts:
                        th3gram_counts[gram_str] = 1
                    else:
                        th3gram_counts[gram_str] += 1

        except AttributeError:
            # Not sure why/how these are cropping up.
            pass
        article = cur.fetchone()
        count += 1
        print("{}/41273".format(count))
    conn.commit()
    return onegram_counts, twogram_counts, th3gram_counts


def collect_term_dictionary_db(conn, min_percent=0.001, max_percent=0.30, testing=False):
    print("collecting ngrams.")
    onegrams, twograms, th3grams = collect_ngrams_db(conn, testing)

    # Need to find the threshold count values for keeping one of the grams
    # First need total number of articles.
    count_sql = "SELECT COUNT(*) FROM news_db_test.article_text;"
    with conn.cursor() as cur:
        cur.execute(count_sql)
        res = cur.fetchone()
    article_count = res[0]
    min_count = max(int(min_percent * article_count), 10)
    max_count = int(max_percent * article_count)
    print("filtering ngrams: max_count {}, min_count {}.".format(max_count, min_count))

    onegrams = dict(filter(lambda e: (e[1] > min_count) and (e[1] < max_count), onegrams.items()))
    twograms = dict(filter(lambda e: (e[1] > min_count) and (e[1] < max_count), twograms.items()))
    th3grams = dict(filter(lambda e: (e[1] > min_count) and (e[1] < max_count), th3grams.items()))

    return onegrams, twograms, th3grams


def make_term_dict(grams):
    # Assume grams is a list of the 1, 2, 3 grams
    term_map = {}
    idx = 0
    for g_list in grams:
        for g in g_list:
            term_map[g] = idx
            idx += 1
    grams[0].update(grams[1])
    grams[0].update(grams[2])
    return term_map, grams[0]


def get_article_term_counts(conn, term_map, testing=False):
    counts = []
    artid_map = {}
    author_map = [] # List of outlet_ids such that outlet(counts[i]) = author_map[i]
    author_set = set() # Set of all the outlet_ids so we can make the needed data objects later.
    art_idx = 0
    N_terms = len(term_map)

    cur = conn.cursor()

    if testing:
        sql = """SELECT art_t.articleid, art_t.extracttext, news_o.name FROM news_db_test.article_text as art_t
                 JOIN news_db_test.news_article as na on art_t.articleid = na.articleid
                 JOIN news_db_test.news_outlet as news_o on na.newsoutletid = news_o.newsoutletid LIMIT 100;"""
    else:
        sql = """SELECT art_t.articleid, art_t.extracttext, news_o.name FROM news_db_test.article_text as art_t
                 JOIN news_db_test.news_article as na on art_t.articleid = na.articleid
                 JOIN news_db_test.news_outlet as news_o on na.newsoutletid = news_o.newsoutletid;"""

    cur.execute(sql)
    article = cur.fetchone()
    while article:
        # We update the counts so they reflect the number of articles each 1,2, and 3 gram shows up in
        try:
            text_tokens = clean_and_split_text(article[1])
            art_ngrams = NgramCounter([nltk.ngrams(text_tokens, 1),
                                       nltk.ngrams(text_tokens, 2),
                                       nltk.ngrams(text_tokens, 3)])
            article_counts = [0 for i in range(N_terms)]

            for term in term_map:
                idx = term_map[term]
                terms = term.split(",")
                if len(terms) == 1:
                    article_counts[idx] = art_ngrams[terms[0]]
                if len(terms) == 2:
                    article_counts[idx] = art_ngrams[[terms[0]]][terms[1]]
                if len(terms) == 3:
                    article_counts[idx] = art_ngrams[(terms[0], terms[1])][terms[2]]

            counts.append(article_counts)
            author_map.append(article[2]) # Should be the newsoutletid
            author_set.add(article[2])
            artid_map[art_idx] = article[0]  # article[0] should be the articleid from the DB
            art_idx += 1  # this is all in case some articles 'fuck up' and get excepted.
            print("finished {}: {}/41273".format(article[0], art_idx))

        except AttributeError:
            pass
        article = cur.fetchone()

    return counts, artid_map, author_map, author_set


def clean_and_split_text(input_txt):
    remove_strs = ["\\\\n", "\\n", "-,", "-", ",,", ",", "!", ".", "-,", "-,,", ",,", ",,,", ",,,,"]
    for s in remove_strs:
        input_txt.replace(s, " ")
    return input_txt.lower().split(" ")


def build_tbip_dataset(conn, path_str, testing=False):
    ones, twos, threes = collect_term_dictionary_db(conn, min_percent=0.01, max_percent=0.3, testing=testing)
    grams = [ones, twos, threes]
    term_map, term_dict = make_term_dict(grams)

    counts, artid_map, author_map, author_set = get_article_term_counts(conn, term_map, testing=testing)

    # vocabulary.txt
    save_vocabtxt(term_map, path_str)

    # author_map.txt, author_indices.npy
    save_author_files(author_map, author_set, path_str)

    # counts.npz
    save_counts_file(counts, path_str)


def save_vocabtxt(term_map, path_str):
    fn = "{}/vocabulary.txt"
    f = open(fn.format(path_str), "w")
    for t in term_map:
        f.write("{}\n".format(t))
    f.close()


def save_author_files(author_map, author_set, path_str):
    author_map_f = open("{}/author_map.txt".format(path_str), "w")
    author_dict = {}
    idx = 0
    for a in author_set:
        author_map_f.write("{}\n".format(a))
        author_dict[a] = idx
        idx += 1
    author_map_f.close()

    author_indicies = []
    for a in author_map:
        author_indicies.append(author_dict[a])

    author_ind_f = open("{}/author_indices.npy".format(path_str), "wb")
    np.save(author_ind_f, np.asarray(author_indicies))
    author_ind_f.close()


def save_counts_file(counts, path_str):
    counts_csr = csr_matrix(np.asarray(counts))
    counts_csr_f = open("{}/counts.npz".format(path_str), "wb")
    save_npz(counts_csr_f, counts_csr)
    counts_csr_f.close()


def get_full_dataset(conn, testing=False):
    if testing:
        sql = """SELECT art_t.articleid, art_t.extracttext, news_o.name FROM news_db_test.article_text as art_t
                 JOIN news_db_test.news_article as na on art_t.articleid = na.articleid
                 JOIN news_db_test.news_outlet as news_o on na.newsoutletid = news_o.newsoutletid LIMIT 100;"""
    else:
        sql = """SELECT art_t.articleid, art_t.extracttext, news_o.name FROM news_db_test.article_text as art_t
                 JOIN news_db_test.news_article as na on art_t.articleid = na.articleid
                 JOIN news_db_test.news_outlet as news_o on na.newsoutletid = news_o.newsoutletid;"""

    cur = conn.cursor()
    cur.execute(sql)
    results = cur.fetchall()
    return results


def remove_cooccurring_ngrams(counts, vocabulary):
    """Remove unigrams and n-grams that co-occur from counts and vocabulary.

    Our data includes both unigrams and n-grams. Since each n-gram consists of
    multiple unigrams, this will result in undesired co-occuruences. For example,
    if we have a bigram of "health care", a document that includes this will
    also include a count for "health" and a count for "care" (in addition to the
    bigram counts). We fix this by subtracting the corresponding unigram counts
    each time an n-gram appears.

    Args:
      counts: A sparse matrix with shape [num_documents, num_words].
      vocabulary: A vector with shape [num_words], containing the vocabulary.

    Returns:
      counts_dense: A dense matrix with shape [num_documents, num_words], where
        the co-occuring n-grams are removed.
    """
    # `n_gram_to_unigram` takes as key an index to an n-gram in the vocabulary
    # and its value is a list of the vocabulary indices of the corresponding
    # unigrams.
    n_gram_indices = np.where(
        np.array([len(word.split(' ')) for word in vocabulary]) > 1)[0]
    n_gram_to_unigrams = {}
    for n_gram_index in n_gram_indices:
        matching_unigrams = []
        for unigram in vocabulary[n_gram_index].split(' '):
            if unigram in vocabulary:
                matching_unigrams.append(np.where(vocabulary == unigram)[0][0])
        n_gram_to_unigrams[n_gram_index] = matching_unigrams

    # `n_grams_to_bigrams` now breaks apart trigrams and higher to find bigrams
    # as subsets of these words.
    n_grams_to_bigrams = {}
    for n_gram_index in n_gram_indices:
        split_n_gram = vocabulary[n_gram_index].split(' ')
        n_gram_length = len(split_n_gram)
        if n_gram_length > 2:
            bigram_matches = []
            for i in range(0, n_gram_length - 1):
                bigram = " ".join(split_n_gram[i:(i + 2)])
                if bigram in vocabulary:
                    bigram_matches.append(np.where(vocabulary == bigram)[0][0])
            n_grams_to_bigrams[n_gram_index] = bigram_matches

    # Go through counts, and remove a unigram each time a bigram superset
    # appears. Also remove a bigram each time a trigram superset appears.
    # Note this isn't perfect: if bigrams overlap (e.g. "global health care"
    # contains "global health" and "health care"), we count them both. This
    # may introduce a problem where we subract a unigram count twice, so we also
    # ensure non-negativity.
    counts_dense = counts.toarray()
    for i in range(len(counts_dense)):
        n_grams_in_doc = np.where(counts_dense[i, n_gram_indices] > 0)[0]
        sub_n_grams = n_gram_indices[n_grams_in_doc]
        for n_gram in sub_n_grams:
            counts_dense[i, n_gram_to_unigrams[n_gram]] -= counts_dense[i, n_gram]
            if n_gram in n_grams_to_bigrams:
                counts_dense[i, n_grams_to_bigrams[n_gram]] -= counts_dense[i, n_gram]
    counts_dense = np.maximum(counts_dense, 0)
    return counts_dense