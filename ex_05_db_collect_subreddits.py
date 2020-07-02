import praw
import mysql.connector
import RedditDataEnrichment.RedditDataEnrichment as rde

reddit = praw.Reddit("data_enrich", user_agent="data_project_ua")
cnx = mysql.connector.connect(user='wpower3', password='power12!', host='127.0.0.1', database='news_db_test')

cnx.close()
