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
