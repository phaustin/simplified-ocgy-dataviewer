# debugging notes

1. setup:

       mamba create --name dash --file your_lock_file
       conda activate dash
       pip install requirements.txt

2. reproduce the bug:


       gunicorn --workers=5 --threads=1 -b 0.0.0.0:8050 app:server

   then visit localhost:8050 in two separate browser windows.  Select a cruise and a couple of
   soundings in one window.  Then select the same cruise in the other window, and rollover a
   sounding point.  You'll see the selections from the other window.


Phil's theory of what's going on.  If you look at https://dash.plotly.com/sharing-data-between-callbacks -- you'll see that they share a dataframe between workers just like we do here: https://github.com/phaustin/simplified-ocgy-dataviewer/blob/main/app.py#L24-L26  The difference is
that they only need to read the data, while our workers need to both read and write,

Solution to try:  enclose the initializer in a function, then call the function in a callback
when nclicks is None so that it only runs once and fills dcc.Store
https://github.com/phaustin/simplified-ocgy-dataviewer/blob/main/app.py#L103  so that each worker
gets a unique copy in their browser.

Notice how covid-xray does this -- they initialize the Store variables to empty dictionaries here:
https://github.com/phaustin/dash-sample-apps/blob/main/dash-covid-xray/app.py#L291-L292

and then fill them in a callback here:

https://github.com/phaustin/dash-sample-apps/blob/main/dash-covid-xray/app.py#L405-L412

To figure out whether you needed to initalize or change the values, you could test to see whether the the dictionary keys were already prexent, or whether the  context had any state at all, and if it was empty, or the keys weren't there, then you need  initialize
the data dictionaries:

https://community.plotly.com/t/help-needed-how-to-check-for-page-first-load-to-change-callback-behaviour/28440/2


Also -- I can't find an example where a figure is declared at module scope instead of drawn from scratch each time within a callback.   I'm thinking of the "updates on hover" example here:

https://dash.plotly.com/interactive-graphing  whare the update_graph callback makes a new figure and returns it.   Again, I think that's because you can't have global state like this:
https://github.com/phaustin/simplified-ocgy-dataviewer/blob/main/app.py#L111-L112

Another example is 
https://github.com/phaustin/dash-sample-apps/blob/main/dash-covid-xray/app.py#L327-L332
where updating creates a new figure in the callback.



