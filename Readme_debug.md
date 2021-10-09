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

Solution to try:  enclose that initializer in a function, then call the function here:
https://github.com/phaustin/simplified-ocgy-dataviewer/blob/main/app.py#L103  so that each worker
gets a unique copy.

