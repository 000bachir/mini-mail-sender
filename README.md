i have this problem where i couldn't import the csv file into supabase since suapbase cannot understand what is ,, and it interprets them as error so
to try and fix i will this linux command :

sed -i 's/,,/,NULL,/g' emails.csv

so the command didn't do much but all i had to do is removed the import of the added at and last contacted and let supabase
handle it form me since : last_contacted_at TIMESTAMP WITH TIME ZONE NULL will do it auto same as added_at





UPDATE ::::::: 
Well i moved from supabase to local database and now i just decided to just use google spread sheet in order to make it easy to populate the file since i really only for now need a file as for the local i will find a use case for it in the near futur but now i need the project finished
