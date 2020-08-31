import pymysql
import ArticleNLP.ArticleNLP as anlp

results_dir_path = "results/full_tbip_dataset"
conn = pymysql.connect(user='wpower3', passwd='power12!', host='127.0.0.1', db='news_db_test')

anlp.build_tbip_dataset(conn, results_dir_path, testing=True)