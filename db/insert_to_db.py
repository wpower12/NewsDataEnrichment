import pymysql
import cryptography
import time
import pandas as pd


############################## ESTABLISH A CONNECTION ###############################
def connection(hostname, username, password, dbName):
    conn = pymysql.connect(host=hostname, user=username, passwd=password,db=dbName)
    return conn
#####################################################################################


################################## END CONNECTION ###################################
def end_connection(conn):
    conn.close()
#####################################################################################


#################################### Read Data ######################################
def read_file (input, file):
    df = pd.read_csv(input + file + '.csv', sep="\t", header=0, engine='python')
    # replace nan values with none (for db purposes)
    df = df.astype(object).where(pd.notnull(df), None)
    return df
#####################################################################################


############################## Insert to DB from file ###############################
def insert_to_db_from_file(conn, df, table):
    cur = conn.cursor()
    cols = "`,`".join([str(i) for i in df.columns.tolist()])
    insert_time = time.time()
    for i, row in df.iterrows():
        sql = "INSERT INTO `" + table + "` (`" + cols + "`) VALUES (" + "%s,"*(len(row)-1) + "%s)"
        cur.execute(sql, tuple(row))
        conn.commit()
    print('Done inserting ' + table)
    print('Inserting time: %s sec' % '{:.6f}'.format(time.time() - insert_time))
    print()
#####################################################################################


############################# Insert to social_network ##############################
def insert_to_social_network(conn, table):
    cur = conn.cursor()
    insert_time = time.time()
    sql = "INSERT INTO `" + table + "` (name, url) VALUES (%s, %s)"
    val = ("Reddit", "https://www.reddit.com/")
    cur.execute(sql, val)
    conn.commit()
    print('Done inserting ' + table)
    print('Inserting time: %s sec' % '{:.6f}'.format(time.time() - insert_time))
    print()
#####################################################################################


####################################### MAIN ########################################
def main():
    # Connect to database
    host = '127.0.0.1'
    username = 'wpower3'
    password = 'power12!'
    dbName = 'news_db_test'
    conn = connection(host, username, password, dbName)

    # Read data from csv file (original db)
    input = 'data/'

    # Insert social network to db
    insert_to_social_network(conn, 'social_network')

    # Read and insert outlets to db
    file = 'outlets'
    df = read_file(input, file)
    table = 'news_outlet'
    insert_to_db_from_file(conn, df, table)

    # Read and insert articles to db
    table = 'news_article'
    # OK: fn, msnbc, nypost, nytimes, tg, wp, wtimes
    # Problem: cnn, dm, npr, reuters, ustoday, wsj
    # All: ['cnn', 'dm', 'fn', 'msnbc', 'npr', 'nypost', 'nytimes', 'reuters', 'tg', 'ustoday', 'wp', 'wsj', 'wtimes']
    articles = ['fn', 'msnbc', 'nypost', 'nytimes', 'tg', 'wp', 'wtimes']
    for a in articles:
        df = read_file(input, a)
        insert_to_db_from_file(conn, df, table)

    # Close connection
    end_connection(conn)

if ( __name__ == "__main__"):
    main()
#####################################################################################