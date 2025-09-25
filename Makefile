server :
	flask --app app.src.index run --debug


check_credentials : 
	python -m app.utils.Check_email_credential


database : 
	python -m app.supabase.supabaseClient

time : 
	python -m app.scheduler 

