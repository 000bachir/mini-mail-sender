# import logging
# from pathlib import Path
# from typing import List, Optional
# from google.oauth2.service_account import Credentials
# import gspread
# SCOPES = [
#     "https://www.googleapis.com/auth/spreadsheets",
#     "https://www.googleapis.com/auth/drive"
# ]
# CREDENTIALS_FILE = Path("app/Credentials/Credentials.json")
#
# logger = logging.getLogger(__name__)
# class GoogleSheetConnection:
#     def __init__(self , enable_loggin : bool ,   scopes : Optional[List[str]] = None  , credential_file : Path = CREDENTIALS_FILE  ) -> None:
#         self.credential_file =  credential_file 
#         self._client = gspread.client 
#         self.scopes =  scopes or SCOPES
#         if enable_loggin : 
#             self.logger = logging.getLogger(__name__)
#             logging.basicConfig(
#                 level=logging.INFO,
#                 format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
#             )
#             self.logger.info("GoogleSheetConnection Class initiated")
#
#
#     def connect(self) : 
#         credentials = Credentials.from_service_account_file(
#             self.credential_file , 
#             scopes = self.scopes
#         )
#         self._client = gspread.authorize(credentials)
#         return self._client
#
#     def get_client(self)  : 
#         if self._client is None : 
#             self.logger.warning("No active client -- connecting now")
#             return self.connect()
#         return self._client
#
#     def open_spreadsheet(self , file_name : str) -> gspread.Spreadsheet : 
#         return self.get_client().open(file_name)
#     def get_worksheet(self , spreadsheet_name : str , worksheet_index : int) : 
#         spreadsheet = self.open_spreadsheet(spreadsheet_name)
#         worksheet = spreadsheet.get_worksheet(worksheet_index)
#         if worksheet is None : 
#             raise IndexError(f"No worksheet at index {worksheet_index} in {spreadsheet_name}")
#
#         return worksheet
#
#
#
#
import logging
from pathlib import Path
from typing import List, Optional

import gspread
from google.oauth2.service_account import Credentials

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
]
CREDENTIALS_FILE = Path("app/Credentials/Credentials.json")

logger = logging.getLogger(__name__)


class GoogleSheetConnection:
    """Lazily-connecting wrapper around a gspread client."""

    def __init__(
        self,
        credentials_file: Path = CREDENTIALS_FILE,
        scopes: Optional[List[str]] = None,
        enable_logging: bool = True,
    ) -> None:
        self.credentials_file = credentials_file
        self.scopes = scopes or SCOPES
        self.enable_logging = enable_logging
        self._client: Optional[gspread.Client] = None

        if self.enable_logging:
            logger.info(
                "GoogleSheetConnection initialized (credentials=%s)",
                self.credentials_file,
            )

    def connect(self) -> gspread.Client:
        """Authenticate and cache a gspread client."""
        credentials = Credentials.from_service_account_file(
            str(self.credentials_file),
            scopes=self.scopes,
        )
        self._client = gspread.authorize(credentials)
        if self.enable_logging:
            logger.info("Connected to Google Sheets API")
        return self._client

    def get_client(self) -> gspread.Client:
        """Return the cached client, connecting first if needed."""
        if self._client is None:
            if self.enable_logging:
                logger.info("No active client — connecting now")
            return self.connect()
        return self._client

    def open_spreadsheet(self, file_name: str) -> gspread.Spreadsheet:
        return self.get_client().open(file_name)

    def get_worksheet(self, spreadsheet_name: str, worksheet_index: int = 0) -> gspread.Worksheet:
        """
        Raises whatever gspread/auth raises naturally (e.g.
        gspread.exceptions.SpreadsheetNotFound) instead of relabeling it —
        callers can catch the real exception type.
        """
        spreadsheet = self.open_spreadsheet(spreadsheet_name)
        worksheet = spreadsheet.get_worksheet(worksheet_index)
        if worksheet is None:
            raise IndexError(
                f"No worksheet at index {worksheet_index} in '{spreadsheet_name}'"
            )
        return worksheet
