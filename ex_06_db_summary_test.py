import praw
import pymysql

import RedditDataEnrichment.RedditDataEnrichment as rde

conn = pymysql.connect(user='wpower3', passwd='power12!', host='127.0.0.1', db='news_db_test')

rde.build_OS_Net_from_outlet_count_db(conn, "test.txt")

conn.close()
