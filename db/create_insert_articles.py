import pymysql
import time
from collections import OrderedDict
import pandas as pd


######################## CREATE DB AND ESTABLISH CONNECTION ########################
def connection(hostname, username, password, dbName):
    conn = pymysql.connect(host=hostname, user=username, passwd=password,db=dbName)
    return conn
#####################################################################################


################################## END CONNECTION ###################################
def end_connection(conn):
    conn.close()
#####################################################################################


################################### CREATE TABLES ###################################
def create_tables(conn):
    cur = conn.cursor()
    tables = OrderedDict()
    tables['ArticleText'] = (
        "CREATE TABLE IF NOT EXISTS `article_text`("
        " `articleid` int(20) NOT NULL,"
        " `extracttext` longtext ,"
        "  PRIMARY KEY (`articleid`),"
        "  CONSTRAINT `news_article_fk1` FOREIGN KEY (`articleid`) "
        "  REFERENCES `news_article` (`articleid`) ON DELETE NO ACTION) ENGINE=InnoDB"
    )

    for name, ddl in tables.items():
        st = time.time()
        cur.execute(ddl)
        print("Creating table {}: ".format(name), end='')
        print('%s sec' % '{:.6f}'.format(time.time() - st))
        conn.commit()

#####################################################################################

#################################### Read Data ######################################
def read_file (input, file):
    df = pd.read_csv(input + file + '_text.csv', sep=",", header=0, encoding='utf-8-sig')
    # replace nan values with none (for db purposes)
    df = df.astype(object).where(pd.notnull(df), None)
    df = df.drop(columns='Unnamed: 0')
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


####################################### MAIN ########################################
def main():
    # Connect to database
    host = '127.0.0.1'
    username = 'wpower3'
    password = 'power12!'
    dbName = 'news_db_test'

    conn = connection(host, username, password, dbName)

    # Create tables and calculate process time
    print('Start Time for creating tables: ', end='')
    start_time = time.time()
    create_tables(conn)
    print('Total time for creating tables: ', end='')
    print('%s sec' % '{:.6f}'.format(time.time() - start_time))

    # Read and insert outlets to db
    dataset = ['fn', 'msnbc', 'nypost', 'nytimes', 'tg', 'wp', 'wtimes']
    path = '../data/'
    for d in dataset:
        df = read_file(path, d)
        table = 'article_text'
        insert_to_db_from_file(conn, df, table)

    # Close connection
    end_connection(conn)

if ( __name__ == "__main__"):
    main()
#####################################################################################