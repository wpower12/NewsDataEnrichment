import praw

import RedditDataEnrichment.RedditDataEnrichment as rde

url_list_fn = "test_data/wsj_2.txt"
sub_list_fn = "results/subs_liberal_conservative_2_TESTDATA.txt"
result_fn   = 'results/tag_test_01_wsj.txt'

reddit = praw.Reddit("data_enrich", user_agent="data_project_ua")

rde.tag_articles(reddit, sub_list_fn, url_list_fn, result_fn)