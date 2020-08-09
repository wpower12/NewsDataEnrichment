import nltk
from nltk.lm import NgramCounter


def collect_ngrams(articles):
    onegram_counts = dict()
    twogram_counts = dict()
    th3gram_counts = dict()

    for index, row in articles.iterrows():
        # We update the counts so they reflect the number of articles each 1,2, and 3 gram shows up in
        try:
            text = row['text'].lower().split(" ")
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
            pass

    return onegram_counts, twogram_counts, th3gram_counts


def collect_term_dictionary(articles, min_percent=0.001, max_percent=0.30):
    print("collecting ngrams.")
    onegrams, twograms, th3grams = collect_ngrams(articles)

    # Need to find the threshold count values for keeping one of the grams
    min_count = int(min_percent*len(articles))
    max_count = int(max_percent*len(articles))
    print("filtering ngrams: max_count {}, min_count {}.".format(max_count, min_count))

    print(onegrams)

    onegrams = dict(filter(lambda e: (e[1] > min_count) and (e[1] < max_count), onegrams.items()))
    twograms = dict(filter(lambda e: (e[1] > min_count) and (e[1] < max_count), twograms.items()))
    th3grams = dict(filter(lambda e: (e[1] > min_count) and (e[1] < max_count), th3grams.items()))

    return onegrams, twograms, th3grams
