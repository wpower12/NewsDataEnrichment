import nltk
from nltk.lm import NgramCounter


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


def collect_ngrams_db(conn):
    cur = conn.cursor()
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


def collect_term_dictionary_db(conn, min_percent=0.001, max_percent=0.30):
    print("collecting ngrams.")
    onegrams, twograms, th3grams = collect_ngrams_db(conn)

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


def get_article_term_counts(conn, term_map):
    counts = []
    artid_map = {}
    art_idx = 0
    N_terms = len(term_map)

    cur = conn.cursor()
    sql = "SELECT * FROM news_db_test.article_text;"
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
            artid_map[art_idx] = article[0]  # article[0] should be the articleid from the DB
            art_idx += 1  # this is all in case some articles 'fuck up' and get excepted.
            print("finished {}: {}/41273".format(article[0], art_idx))

        except AttributeError:
            pass
        article = cur.fetchone()

    return counts, artid_map


def clean_and_split_text(input_txt):
    remove_strs = ["\\n", "-,", "-", ",,", ",", "!"]
    for s in remove_strs:
        input_txt.replace(s, " ")
    return input_txt.lower().split(" ")
