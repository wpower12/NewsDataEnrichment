import pymysql
import time
from collections import OrderedDict


######################## CREATE DB AND ESTABLISH CONNECTION ########################
def connection(hostname, username, password, dbName):
    conn = pymysql.connect(host=hostname, user=username, passwd=password)
    cur = conn.cursor()
    cur.execute("DROP DATABASE IF EXISTS %s" % (dbName))
    cur.execute("CREATE DATABASE IF NOT EXISTS {} DEFAULT CHARACTER SET 'UTF8MB4'".format(dbName))
    conn.close()
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
    tables['NewsOutlet'] = (
        "CREATE TABLE IF NOT EXISTS `news_outlet`("
        " `newsoutletid` int(20) NOT NULL,"
        " `name` varchar(500),"
        " `url` varchar(500),"
        "  PRIMARY KEY (`newsoutletid`))ENGINE=InnoDB"
    )
    tables['NewsArticle'] = (
        "CREATE TABLE IF NOT EXISTS `news_article`("
        " `articleid` int(20) NOT NULL,"
        " `title` varchar(500),"
        " `url` varchar(500),"
        " `googletime` varchar(100),"
        " `publishtime` varchar(100),"
        " `newsoutletid` int(20),"
        "  PRIMARY KEY (`articleid`),"
        "  CONSTRAINT `outlet_article_fk1` FOREIGN KEY (`newsoutletid`) "
        "  REFERENCES `news_outlet` (`newsoutletid`) ON DELETE NO ACTION) ENGINE=InnoDB"
    )
    tables['SocialNetwork'] = (
        "CREATE TABLE IF NOT EXISTS `social_network`("
        " `socialnetworkid` int(20) NOT NULL AUTO_INCREMENT,"
        " `name` varchar(500),"
        " `url` varchar(500),"
        "  PRIMARY KEY (`socialnetworkid`))ENGINE=InnoDB"
    )
    tables['SocialGroup'] = (
        "CREATE TABLE IF NOT EXISTS `social_group`("
        " `socialgroupid` varchar(200) NOT NULL,"
        " `name` varchar(500),"
        " `description` text ,"
        " `url` varchar(500),"
        " `numberofsubscribers` int(20),"
        " `publishtime` varchar(100),"
        " `socialnetworkid` int(20) ,"
        "  PRIMARY KEY (`socialgroupid`),"
        "  CONSTRAINT `social_group_fk1` FOREIGN KEY (`socialnetworkid`) " 
        "  REFERENCES `social_network` (`socialnetworkid`) ON DELETE NO ACTION) ENGINE=InnoDB"
    )
    tables['User'] = (
        "CREATE TABLE IF NOT EXISTS `user`("
        " `userid` varchar(200) NOT NULL,"
        " `username` varchar(500) NOT NULL,"
        " `url` varchar(500),"
        " `karmapoints` int(20),"
        " `dateofbirth` int(100),"
        "  PRIMARY KEY (`userid`)) ENGINE=InnoDB"
    )
    tables['Thread'] = (
        "CREATE TABLE IF NOT EXISTS `thread`("
        " `threadid` varchar(200) NOT NULL,"
        " `url` varchar(500),"
        " `userid` varchar(200) ,"
        " `title` varchar(500),"
        " `description` text,"
        " `publishtime` int(20),"
        " `tag` varchar(100),"
        " `socialgroupid` varchar(200),"
        " `articleid` int(20),"
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
        " `commentid` varchar(200) NOT NULL,"
        " `parentid` int(20) ,"
        # " `url` varchar(500),"
        " `userid` varchar(200),"
        " `numpoints` int(20),"
        " `text` text,"
        " `publishtime` int(100),"
        " `threadid` varchar(200) ,"
        "  PRIMARY KEY (`commentid`),"
        "  CONSTRAINT `user_comment_fk1` FOREIGN KEY (`userid`) "
        "  REFERENCES `user` (`userid`) ON DELETE NO ACTION ,"
        "  CONSTRAINT `thread_comment_fk2` FOREIGN KEY (`threadid`) "
        "  REFERENCES `thread` (`threadid`) ON DELETE NO ACTION) ENGINE=InnoDB"
    )
    # tables['Query'] = (
    #     "CREATE TABLE IF NOT EXISTS `query`("
    #     " `queryid` int(20) NOT NULL AUTO_INCREMENT,"
    #     " `query` text ,"
    #     " `threadid` int(20) ,"
    #     "  PRIMARY KEY (`queryid`),"
    #     "  CONSTRAINT `thread_query_fk1` FOREIGN KEY (`threadid`) "
    #     "  REFERENCES `thread` (`threadid`) ON DELETE NO ACTION) ENGINE=InnoDB"
    # )

    for name, ddl in tables.items():
        st = time.time()
        cur.execute(ddl)
        print("Creating table {}: ".format(name), end='')
        print('%s sec' % '{:.6f}'.format(time.time() - st))
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

    # Create tables and calculate process time
    print('Start Time for creating tables: ', end='')
    start_time = time.time()
    create_tables(conn)
    print('Total time for creating tables: ', end='')
    print('%s sec' % '{:.6f}'.format(time.time() - start_time))

    # Close connection
    end_connection(conn)

if ( __name__ == "__main__"):
    main()
#####################################################################################