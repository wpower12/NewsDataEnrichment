import praw
import prawcore
import networkx as nx
from networkx.algorithms import bipartite
import matplotlib.pyplot as plt
import pandas as pd


def collect_subreddits_txt(reddit, depth, seeds, sublist_fn):
    # TODO - Update this to be a set, add a forbiddens set, return the difference at the end? idk. 
    f = open(sublist_fn, 'w')
    sub_list = []
    for seed_sub in seeds:
        seed = reddit.subreddit(seed_sub)
        subs_to_process = [seed]
        # 'depth 0' is adding just the  seed to the list, so we have to go to 1 more than depth in our range.
        for d in range(depth + 1):
            print("Processing: {}".format(subs_to_process))
            temp_list = []
            for s in subs_to_process:
                try:
                    f.write("{}, {}\n".format(s.display_name, s.subscribers))
                    for widget in s.widgets.sidebar:
                        if isinstance(widget, praw.models.CommunityList):
                            temp_list.extend(widget)
                            break
                except prawcore.exceptions.Forbidden:
                    print("Forbidden Sub: {}".format(s.display_name))
            subs_to_process = temp_list
    f.close()
    print("Full set of subreddits saved to: {}".format(sublist_fn))


def collect_subreddits(reddit, depth, seeds):
    sub_list = set()
    forbiddens = set()
    for seed_sub in seeds:
        seed = reddit.subreddit(seed_sub)
        subs_to_process = [seed]
        # 'depth 0' is adding just the  seed to the list, so we have to go to 1 more than depth in our range.
        for d in range(depth + 1):
            print("Processing: {}".format(subs_to_process))
            temp_list = []
            for s in subs_to_process:
                try:
                    sub_list.add(s)
                    for widget in s.widgets.sidebar:
                        if isinstance(widget, praw.models.CommunityList):
                            temp_list.extend(widget)
                            break
                except prawcore.exceptions.Forbidden:
                    forbiddens.add(s)
                    print("col_subs - Forbidden Sub: {}".format(s.display_name))
            subs_to_process = temp_list

    return list(sub_list.difference(forbiddens))


def tag_articles(reddit, sublist_fn, article_list_fn, outlet_summary_fn):
    # First just grab the sub list.
    sublist_f   = open(sublist_fn, 'r')
    sub_list = []
    sublist_f.readline()  # Read off the 'label row'
    for line in sublist_f:
        res = line.split(',')
        res[1] = int(res[1].rstrip('\n'))
        sub_list.append(res)
    sublist_f.close()

    # Now build 'results' list. Instead of making the SQL query, we can just write to a file for now?
    url_list_f  = open(article_list_fn, 'r')
    result_file = open(outlet_summary_fn, 'w')

    url_list_f.readline()
    curr_line = 1
    counts = {}
    for s in sub_list:
        counts[s[0]] = 0

    while True:
        curr_line += 1
        line = url_list_f.readline()
        if line == "":
            break

        data_row = line.split('	')
        if len(data_row) <= 1:
            break
        url = data_row[1]
        print(url)
        article_sub_tags = []  # The list of subs that have the article in them.

        # Check each sub in the sub list for the url
        for sub in sub_list:
            sub_name = sub[0]
            sub_obj = reddit.subreddit(sub_name)
            search_res = sub_obj.search("url:{}".format(url))
            if len(list(search_res)) > 0:
                print("\tfound url in {}".format(sub_name))
                article_sub_tags.append(sub_name)
                counts[sub_name] += 1

        # Log the tags for the URL
        # TODO - This is where we'd make the SQL query?

    # Save the counts file to the output file.
    for c in counts:
        result_file.write("{}, {}\n".format(c, counts[c]))

    url_list_f.close()
    result_file.close()


def tag_articles_save_URLs(reddit, sublist_fn, article_list_fn, outlet_summary_fn):
    # First just grab the sub list.
    sublist_f   = open(sublist_fn, 'r')
    sub_list = []
    sublist_f.readline()  # Read off the 'label row'
    for line in sublist_f:
        res = line.split(',')
        res[1] = int(res[1].rstrip('\n'))
        sub_list.append(res)
    sublist_f.close()

    # Now build 'results' list. Instead of making the SQL query, we can just write to a file for now?
    url_list_f  = open(article_list_fn, 'r')
    result_file = open(outlet_summary_fn, 'w')

    url_list_f.readline()
    curr_line = 1
    counts = {}
    for s in sub_list:
        counts[s[0]] = 0

    while True:
        curr_line += 1
        line = url_list_f.readline()
        if line == "":
            break

        data_row = line.split('	')
        if len(data_row) <= 1:
            break
        url = data_row[1]
        print(url)
        article_sub_tags = []  # The list of subs that have the article in them.

        # Check each sub in the sub list for the url
        for sub in sub_list:
            sub_name = sub[0]
            sub_obj = reddit.subreddit(sub_name)
            search_res = sub_obj.search("url:{}".format(url))
            if len(list(search_res)) > 0:
                print("\tfound url in {}".format(sub_name))
                article_sub_tags.append(sub_name)
                counts[sub_name] += 1
                result_file.write("{}, {}\n".format(url, sub_name))

    url_list_f.close()
    result_file.close()


def build_OS_Net_from_outlet_counts(outlet_summaries, result_fn):
    # Assume that outlet summaries is a list of pairs ("<outlet_name>", outlet_summary_fn)

    outlet_nodes = []
    subreddit_nodes = set()
    edge_list = []
    for outlet in outlet_summaries:
        outlet_name, outlet_sum_fn = outlet
        outlet_nodes.append(outlet_name)

        outlet_sum_f = open(outlet_sum_fn, 'r')
        for line in outlet_sum_f:
            line_elements = line.split(", ")
            sub = line_elements[0]
            count = int(line_elements[1])
            if count > 0:
                print((outlet_name, sub, count))
                subreddit_nodes.add(sub)
                edge_list.append((outlet_name, sub, count))

    os_g = nx.Graph()
    os_g.add_nodes_from(outlet_nodes, bipartite=0)
    os_g.add_nodes_from(list(subreddit_nodes), bipartite=1)
    os_g.add_weighted_edges_from(edge_list)

    os_g_largest = os_g.subgraph(sorted(nx.connected_components(os_g), key=len, reverse=True)[0]).copy()

    top = nx.bipartite.sets(os_g_largest)[0]
    pos = nx.bipartite_layout(os_g_largest, top)

    fig, ax = plt.subplots(1, 1, figsize=(8, 6))
    nx.draw_networkx(os_g_largest, ax=ax, pos=pos)
    plt.show()

    result_f = open(result_fn, 'w')
    for e in edge_list:
        result_f.write("{}\n".format(e))

    result_f.close()


def reddit_enrichment(reddit, db, depth, seeds):
    # Returns a list of the collected subs. Each element is a PRAW object that can be searched.
    subs = collect_subreddits(reddit, depth, seeds)

    # Adding the collected subreddits to the social_groups table.
    # IGNOREing the duplicates.
    with db.cursor() as cur:
        sub_query = "INSERT IGNORE INTO social_group (socialgroupid, name) VALUES\n"
        values = []
        for s in subs:
            try:
                values.append(s.id)
                values.append(s.display_name)
                sub_query += "(%s, %s),\n"
            except prawcore.exceptions.Forbidden:
                print("rde - Forbidden Sub: {}".format(s.display_name))

        sub_query = sub_query.rstrip(",\n")+";"
        cur.execute(sub_query, values)
        db.commit()

    with db.cursor() as cur:
        art_query = "SELECT `articleid`, `url` FROM news_article;"
        cur.execute(art_query)

        article = cur.fetchone()
        count = 0
        while article:
            url = article[1]
            thread_list = []
            for sub in subs:
                try:
                    sub_name = sub.display_name
                    sub_obj = reddit.subreddit(sub_name)
                    for thread in sub_obj.search("url:{}".format(url)):
                        thread_list.append([thread, sub_obj.id])

                except prawcore.exceptions.Forbidden:
                    print("f")
                    pass

            print(count, article, thread_list)

            if len(thread_list) > 0:
                # Create the INSERT query for this article.
                # INSERT (threadid, url, articleid, socialgroupid) INTO thread VALUES ...
                # Use the PRAW object id for the thread id, use the same articleid, use 1 for reddit for socialgroupid)w
                thread_query = "INSERT IGNORE INTO thread (threadid, url, articleid, socialgroupid) VALUES\n"
                vals = []
                for t in thread_list:
                    thread, sub_id = t
                    thread_query += "(%s, %s, %s, %s)\n"
                    vals.append(thread.id)
                    vals.append(thread.url)
                    vals.append(article[0])
                    vals.append(sub_id)
                thread_query = thread_query.rstrip("\n")+";"
                print(thread_query)
                cur.execute(thread_query, vals)

            count += 1
            article = cur.fetchone()
        db.commit()


def reddit_enrichment_v2(reddit, conn, depth, seeds):
    cur = conn.cursor()
    subs = collect_subreddits(reddit, depth, seeds)

    # UPDATING social_groups TABLE - Adding the collected groups subreddits to the social_groups table.
    table = 'social_group'
    sn_id = 1 # fixed value since we are collecting from one social network - Reddits sn_id #
    columns = ['socialgroupid', 'name', 'description', 'url', 'numberofsubscribers', 'publishtime', 'socialnetworkid']
    sub_values = pd.DataFrame(columns=columns)
    for s in subs:
        try:
            sub_values = sub_values.append({'socialgroupid': s.id,
                                            'name': s.display_name,
                                            'description': s.description,
                                            'url': "www.reddit.com/r/{}".format(s.display_name),
                                            'socialnetworkid': sn_id}, ignore_index=True)
        except prawcore.exceptions.Forbidden:
            print("rde - Forbidden Sub: {}".format(s.display_name))

    # replace nan values with none and clean up cols object
    sub_values = sub_values.astype(object).where(pd.notnull(sub_values), None)
    cols = "`,`".join([str(i) for i in sub_values.columns.tolist()])

    # insert values into "social_groups" table
    for i, row in sub_values.iterrows():
        sql = "INSERT IGNORE INTO `" + table + "` (`" + cols + "`) VALUES (" + "%s," * (len(row) - 1) + "%s)"
        cur.execute(sql, tuple(row))
        conn.commit()
    print('Done inserting ' + table)

    # UPDATING THREAD TABLE - Find posts in reddit and adding them to thread table.
    table = 'news_article'

    # FULL QUERY - All articles, uncomment when we leave testing
    art_query = "SELECT `articleid`, `url` FROM `" + table + "` ;"

    # TEST QUERY - Smaller subset of articles, from a single outlet. Comment out when we leave testing
    # outlet_id = 173
    # art_query = "SELECT `articleid`, `url` FROM `" + table + "` WHERE `newsoutletid` = " + str(outlet_id) + \
    #             " AND ( `articleid` = 241 or `articleid` = 561 or `articleid` = 1367 " + \
    #             "or `articleid` = 6147 or `articleid` = 12327 or `articleid` = 24359 " + \
    #             "or `articleid` = 31174 or `articleid` = 31349 or `articleid` = 89298 " + \
    #             "or `articleid` = 1554723) ;"

    cur.execute(art_query)
    article = pd.DataFrame(cur.fetchall())

    # change article object to tuples composed of [[articleid, url]]
    urls = list(zip(article[0].tolist(), article[1].tolist()))

    # search for related posts and save it to thread list
    # columns = ['threadid', 'url', 'userid', 'title', 'description', 'publishtime', 'tag',
    #            'socialgroupid', 'articleid']

    columns = ['threadid', 'url', 'title', 'publishtime', 'socialgroupid', 'articleid']
    cols = "`,`".join([str(i) for i in columns])
    table = 'thread'

    # thread_values = pd.DataFrame(columns=columns)
    for i in urls:
        for sub in subs:
            try:
                sub_name = sub.display_name
                sub_obj = reddit.subreddit(sub_name)
                for thread in sub_obj.search("url:{}".format(i[1])):
                    thread_values = [thread.id,
                                     thread.permalink,
                                     thread.title,
                                     thread.created_utc,
                                     sub_obj.id,
                                     i[0]]          # Article ID

                    sql = "INSERT IGNORE INTO `" + table + "` (`" + cols + "`) VALUES (%s, %s, %s, %s, %s, %s );"
                    cur.execute(sql, thread_values)
                    conn.commit()
                    print("Inserted Thread: {}".format(thread.title))

            # Forbidden to access by reddit
            except prawcore.exceptions.Forbidden:
                print("f")
                pass

    print('Done inserting ' + table)

