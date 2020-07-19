import praw
import pymysql

import RedditDataEnrichment.RedditDataEnrichment as rde

DEPTH = 1
SEEDS = ['liberal', 'conservative']

reddit = praw.Reddit("data_enrich", user_agent="data_project_ua")
conn = pymysql.connect(user='wpower3', passwd='power12!', host='127.0.0.1', db='news_db_test')

rde.reddit_enrichment_v2(reddit, conn, DEPTH, SEEDS)

conn.close()
