server : 
	fastapi dev main.py
run : 
	cd . && python -m app.src.main
# test commands 
testSender : 
	cd . && python -m pytest app/Mailer/test_email_sender.py
supabase_test : 
	cd . && python -m pytest app/supabase/test_supabase_client.py
scheduler_test : 
	cd . && python -m pytest app/scheduler/test_scheduler.py

# deleting pycahe folder from the project : 
clean : 
	find . -type d -name "__pycahe__" -exec rm -r {} +
	find . -type f -name "*.pyc" -delete
