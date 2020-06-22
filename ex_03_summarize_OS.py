import RedditDataEnrichment.RedditDataEnrichment as rde

outlets = [('fox', 'results/subcounts_fn_00.txt'),
           ('wsj', 'results/subcounts_wsj_00.txt'),
           ('nyt', 'results/subcounts_nyt_00.txt'),
           ('wp',  'results/subcounts_wp_00.txt')]

rde.build_OS_Net_from_outlet_counts(outlets, "results/full_sum_test.txt")

