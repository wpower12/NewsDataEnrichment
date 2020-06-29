import pymysql

outlets = [('fox', 0, '../test_data/fn_2.txt',  'results/subcounts_fn_00.txt'),
           ('wsj', 1, '../test_data/wsj_2.txt', 'results/subcounts_wsj_00.txt'),
           ('wp',  2, '../test_data/wp_2.txt',  'results/subcounts_wp_00.txt'),
           ('nyt', 3, '../test_data/nyt_2.txt', 'results/subcounts_nyt_00.txt')]


def insert_articles(db, outlet_id, article_list_fn):
    f = open(article_list_fn, 'r')
    f.readline()  # Get the header off.
    insert_str = ""
    for line in f:
        line_elms = line.split("\t") # SPLIT ON TABS!
        art_id = line_elms[0]
        art_url = line_elms[1]
        # INSERT (URL, NewsOutletID)
        insert_str += "('{}', '{}', 'title'),\n".format(art_url, outlet_id)

    insert_str = insert_str.rstrip(",\n")
    f.close()
    art_query = "INSERT INTO news_db_test.news_article (url, newsoutletid, title) VALUES " + insert_str + ";"

    cur = db.cursor()
    cur.execute(art_query)
    db.commit()


host = '127.0.0.1'
username = 'wpower3'
password = 'power12!'
dbName = 'news_db_test'
conn = pymysql.connect(host=host, user=username, passwd=password)

for o in outlets:
    _, o_id, art_fn, _ = o
    insert_articles(conn, o_id, art_fn)




