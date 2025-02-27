# ct_sniper
# Stop Running
heroku ps:scale worker=0 -a ct-sniper

# Start running
heroku ps:scale worker=1 -a ct-sniper



# Need a better solution to the scraper -- nitter stuff gets blocked somtimes. https://status.d420.de/
# Change code to nitter.space atm, but maybe