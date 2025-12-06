server : 
	fastapi dev main.py
email : 
	python -m app.Mailer.sender
check_credentials : 
	python -m app.utils.Check_email_credential
database : 
	python -m app.supabase.supabaseClient
time : 
	python -m app.scheduler.scheduler.py 
testSender : 
	python -m unittest app.Mailer.test_email_sender
supabase_test : 
	cd . && python -m pytest app/supabase/test_supabase_client.py

scheduler_test : 
	cd . && python -m pytest app/scheduler/test_scheduler.py
