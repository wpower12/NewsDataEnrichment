import praw
import RedditDataEnrichment.RedditDataEnrichment as rde

sublist_fn = "results/subs_liberal_conservative_2_TESTDATA.txt"
outlets = [('fox', 'test_data/fn_2.txt',  'results/sub_urls_fn_00.txt'),
           ('wsj', 'test_data/wsj_2.txt', 'results/sub_urls_wsj_00.txt'),
           ('nyt', 'test_data/nyt_2.txt', 'results/sub_urls_nyt_00.txt'),
           ('wp',  'test_data/wp_2.txt',  'results/sub_urls_wp_00.txt')]

reddit = praw.Reddit("data_enrich", user_agent="data_project_ua")

for outlet in outlets:
    name, url_list_fn, results_fn = outlet
    rde.tag_articles_save_URLs(reddit, sublist_fn, url_list_fn, results_fn)
    print("summary for {} saved at {}".format(name, results_fn))
