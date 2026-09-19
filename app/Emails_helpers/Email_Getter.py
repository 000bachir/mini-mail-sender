import gspread
from google.oauth2.service_account import Credentials
from utils.Check_email_credential import Credentials_manager

print(Credentials_manager)



SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]
CREDENTIALS_FILE = "app/Credentials/Credentials.json"

def get_sheet_client() : 
     creds = Credentials.from_service_account_file(CREDENTIALS_FILE , scopes=SCOPES)
     return gspread.authorize(creds)
def get_emails(sheet_name : str = "test_contacts" , worksheet_index : int = 0) : 
     client = get_sheet_client()
     sheet = client.open(sheet_name).get_worksheet(worksheet_index)

     headers = sheet.row_values(1)
     if "email" not in [h.strip().lower() for h in headers]:
         raise ValueError(f"No 'email' column found in headers: {headers}")

     col_index = [h.strip().lower() for h in headers].index("email") + 1  # gspread is 1-indexed
     emails = sheet.col_values(col_index)[1:]  # skip header row
     emails = [e for e in emails if e]  # drop blanks

     print(f"Found {len(emails)} emails")
     for e in emails:
         print(e)
     return emails
def append_row(sheet_name : str , row : list) :
     client = get_sheet_client()
     sheet = client.open(sheet_name).sheet1
     sheet.append_row(row)



if __name__ == "__main__" : 
    get_emails("test_contacts")



