# News Data Enrichment
Adding additional 'aggregation' data to the News Article-Outlet dataset. This new aggregation data are the locations (on online social aggregation sites like reddit and facebook) where the articles present in the DB have been shared. 

Currently, only reddit is used as a source for aggregation data, but plans have been made to include public facebook groups as well.

To use the current reddit-based methods, the user must provide a praw.ini file containing a reddit id and secret key. This enables access to the reddit API. Documentation for creating a new 'app' and getting this id and key  can be found [here](https://www.reddit.com/prefs/apps).

The key and secret should be in a file named praw.ini in the top level directory, similar to this:

    [data_enrich]
    client_id=<<CLIENT ID HERE>>
    client_secret=<<SECRET KEY HERE>>
    
To ensure the scripts work, make sure that the 'appname' stays as 'data_enrich'. This is only a local name, and just needs to match in the .ini file itself. You do not need to name the app on the reddit API request page 'data_enrich'.

This repo also contains a folder of scripts and data intended to help get a local test database up and running. Users may
need to change the credentials int he two scripts to match those of their local DB. 
