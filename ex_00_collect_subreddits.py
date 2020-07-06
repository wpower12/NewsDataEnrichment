import praw
from datetime import datetime
import RedditDataEnrichment.RedditDataEnrichment as rde

depth = 2
seeds = ['liberal', 'conservative']
sublist_fn = "results/sublist_liberal_conservative_2_{}.txt".format(datetime.now().strftime("%d%m%Y_%H_%M_%S"))
reddit = praw.Reddit("data_enrich", user_agent="data_project_ua")

rde.collect_subreddits_txt(reddit, depth, seeds, sublist_fn)
