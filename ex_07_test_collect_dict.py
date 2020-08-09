import ArticleNLP.ArticleNLP as anlp
import pandas as pd

# Get some articles from the test
article_f = open('data/NewsArticles.csv', encoding="latin-1")
articles = pd.read_csv(article_f)

onegrams, twograms, th3grams = anlp.collect_term_dictionary(articles[:100])
