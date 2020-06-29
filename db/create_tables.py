import pymysql
import time
from collections import OrderedDict

############################## ESTABLISH A CONNECTION ###############################
def connection(hostname, username, password, dbName):
    conn = pymysql.connect(host=hostname, user=username, passwd=password)
    cur = conn.cursor()
    cur.execute("DROP DATABASE IF EXISTS %s" % (dbName))
    cur.execute("CREATE DATABASE IF NOT EXISTS {} DEFAULT CHARACTER SET 'UTF8MB4'".format(dbName))
    conn.close()
    conn = pymysql.connect(host=hostname, user=username, passwd=password,db=dbName)
    return conn

#####################################################################################

################################### CREATE TABLES ###################################
def create_tables(conn):
    cur = conn.cursor()
    tables = OrderedDict()
    tables['NewsOutlet'] = (
        "CREATE TABLE IF NOT EXISTS `news_outlet`("
        " `newsoutletid` int(10) NOT NULL,"
        " `name` varchar(50) NOT NULL,"
        " `url` varchar(300) NOT NULL,"
        "  PRIMARY KEY (`newsoutletid`))ENGINE=InnoDB"
    )
    tables['NewsArticle'] = (
        "CREATE TABLE IF NOT EXISTS `news_article`("
        " `articleid` int(10) AUTO_INCREMENT PRIMARY KEY,"
        " `title` varchar(200) NOT NULL,"
        " `url` varchar(300) NOT NULL,"
        " `googletime` varchar(20),"
        " `publishtime` varchar(20),"
        " `newsoutletid` int(10),"
        # "  PRIMARY KEY (`articleid`),"
        "  CONSTRAINT `outlet_article_fk1` FOREIGN KEY (`newsoutletid`) "
        "  REFERENCES `news_outlet` (`newsoutletid`) ON DELETE NO ACTION) ENGINE=InnoDB"
    )
    tables['SocialNetwork'] = (
        "CREATE TABLE IF NOT EXISTS `social_network`("
        " `socialnetworkid` int(10) NOT NULL AUTO_INCREMENT,"
        " `name` varchar(100) NOT NULL,"
        " `url` varchar(300) NOT NULL,"
        "  PRIMARY KEY (`socialnetworkid`))ENGINE=InnoDB"
    )
    tables['SocialGroup'] = (
        "CREATE TABLE IF NOT EXISTS `social_group`("
        " `socialgroupid` int(10) NOT NULL AUTO_INCREMENT,"
        " `name` varchar(100) NOT NULL,"
        " `description` text ,"
        " `url` varchar(300) NOT NULL ,"
        " `numberofsubscribers` int(10),"
        " `publishtime` varchar(20),"
        " `socialnetworkid` int(10) ,"
        "  PRIMARY KEY (`socialgroupid`),"
        "  CONSTRAINT `social_group_fk1` FOREIGN KEY (`socialnetworkid`) " 
        "  REFERENCES `social_network` (`socialnetworkid`) ON DELETE NO ACTION) ENGINE=InnoDB"
    )
    tables['User'] = (
        "CREATE TABLE IF NOT EXISTS `user`("
        " `userid` int(10) NOT NULL AUTO_INCREMENT,"
        " `username` varchar(100) NOT NULL,"
        " `url` varchar(300) NOT NULL ,"
        " `karmapoints` int(10),"
        " `dateofbirth` int(10),"
        "  PRIMARY KEY (`userid`)) ENGINE=InnoDB"
    )
    tables['Thread'] = (
        "CREATE TABLE IF NOT EXISTS `thread`("
        " `threadid` int(10) NOT NULL AUTO_INCREMENT,"
        " `url` varchar(300) NOT NULL ,"
        " `userid` int(10) ,"
        " `title` varchar(200),"
        " `description` text,"
        " `publishtime` int(10),"
        " `tag` varchar(50),"
        " `socialgroupid` int(10),"
        " `articleid` int(10),"
        "  PRIMARY KEY (`threadid`),"
        "  CONSTRAINT `user_thread_fk1` FOREIGN KEY (`userid`) " 
        "  REFERENCES `user` (`userid`) ON DELETE NO ACTION ,"
        "  CONSTRAINT `group_thread_fk2` FOREIGN KEY (`socialgroupid`) "
        "  REFERENCES `social_group` (`socialgroupid`) ON DELETE NO ACTION,"
        "  CONSTRAINT `newsarticle_thread_fk3` FOREIGN KEY (`articleid`) "
        "  REFERENCES `news_article` (`articleid`) ON DELETE NO ACTION) ENGINE=InnoDB"
    )
    tables['comment'] = (
        "CREATE TABLE IF NOT EXISTS `comment`("
        " `commentid` int(10) NOT NULL AUTO_INCREMENT,"
        " `parentid` int(10) ,"
        " `url` varchar(300) NOT NULL ,"
        " `userid` int(10) NOT NULL,"
        " `numpoints` int(10),"
        " `text` text,"
        " `publishtime` int(10),"
        " `threadid` int(10) ,"
        "  PRIMARY KEY (`commentid`),"
        "  CONSTRAINT `user_comment_fk1` FOREIGN KEY (`userid`) "
        "  REFERENCES `user` (`userid`) ON DELETE NO ACTION ,"
        "  CONSTRAINT `thread_comment_fk2` FOREIGN KEY (`threadid`) "
        "  REFERENCES `thread` (`threadid`) ON DELETE NO ACTION) ENGINE=InnoDB"
    )
    tables['Query'] = (
        "CREATE TABLE IF NOT EXISTS `query`("
        " `queryid` int(10) NOT NULL AUTO_INCREMENT,"
        " `query` text ,"
        " `threadid` int(10) ,"
        "  PRIMARY KEY (`queryid`),"
        "  CONSTRAINT `thread_query_fk1` FOREIGN KEY (`threadid`) "
        "  REFERENCES `thread` (`threadid`) ON DELETE NO ACTION) ENGINE=InnoDB"
    )
    tables['InsertTestOutlets'] = (
        "INSERT INTO news_outlet (newsoutletid, name, url) VALUES "
        "(0, 'fn', 'fox.com'), "
        "(1, 'wsj', 'wsj.com'), "
        "(2, 'wp', 'wp.com'), "
        "(3, 'nyt', 'nyt.com');"
    )


    for name, ddl in tables.items():
        cur.execute(ddl)
        print("Creating table {}: ".format(name), end='')
        print(time.process_time())
        conn.commit()

#####################################################################################

####################################### MAIN ########################################
def main():
    # Connect to database
    host = '127.0.0.1'
    username = 'wpower3'
    password = 'power12!'
    dbName = 'news_db_test'
    conn = connection(host, username, password, dbName)

    print('Start Time for creating tables: ', end='')
    start_CT = time.process_time()
    print(start_CT)
    create_tables(conn)
    print('End Time for creating tables: ', end='')
    print(time.process_time() - start_CT)

if ( __name__ == "__main__"):
    main()
#####################################################################################