import praw
import prawcore
import networkx as nx
from networkx.algorithms import bipartite
import matplotlib.pyplot as plt


def collect_subreddits(reddit, depth, seeds, sublist_fn):
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


def reddit_enrichment(db, reddit, query):
    seed_subs, where_str = query

    # Create new entry in the query table, save the queryID

    # Gather list of subreddits, add to the metadata for the same query.

    # Insert subreddits into the SocialGroups table, if unique

    # Use where str to gather all the articles

    # Iterate over articles
        # When there is a 'hit' add a new 'row' to the 'insert string' for a final query
        # "INSERT INTO Thread ... (URL, Title, SocialGroupID, ArticleID)
        # Save the ThreadID in a list?

    # Push all the new threads to the DB

    # Add all ThreadIDs to the Query Table -> (QueryID, Query, ThreadID)
