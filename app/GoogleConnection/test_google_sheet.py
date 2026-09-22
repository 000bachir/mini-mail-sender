from pathlib import Path 
from unittest.mock import Mock , MagicMock , patch
import gspread
import pytest
from .google_sheet_connection import GoogleSheetConnection , SCOPES , CREDENTIALS_FILE


@pytest.fixture

def conn() : 
    return GoogleSheetConnection(enable_logging=False)

def test_init_sets_defaults(conn) : 
    assert conn.credentials_file == CREDENTIALS_FILE
    assert conn.scopes == SCOPES 
    assert conn._client == None




def test_init_with_custom_credentials_and_scopes() : 
    different_path = Path("test/credential.json")
    different_scopes = [
        "https://www.googleapis.com/auth/drive/readonly"
    ]
    conn = GoogleSheetConnection(
        credentials_file=different_path ,
        scopes= different_scopes,
        enable_logging=False
    )
    assert conn.credentials_file == different_path
    assert conn.scopes == different_scopes


@patch("app.GoogleConnection.google_sheet_connection.gspread.authorize")
@patch("app.GoogleConnection.google_sheet_connection.Credentials.from_service_account_file")
def test_connect_build_client_from_credentials(mock_from_file , mock_authorize , conn) :
    mock_creds = MagicMock()
    mock_from_file.return_value = mock_creds 
    mock_client = MagicMock()
    mock_authorize.return_value = mock_client

    result = conn.connect() 
    mock_from_file.assert_called_once_with(str(conn.credentials_file) , scopes = conn.scopes)
    mock_authorize.assert_called_once_with(mock_creds)
    assert result is mock_client
    assert conn._client is mock_client

@patch.object(GoogleSheetConnection , "connect")
def test_get_client_connects_when_no_cached_client(mock_connect , conn) : 
    mock_client = MagicMock()
    mock_connect.return_value = mock_client

    result = conn.get_client()
    mock_connect.assert_called_once()
    assert result is mock_client


@patch.object(GoogleSheetConnection , "connect")
def test_resuses_cached_client_without_reconnecting(mock_connect , conn) : 
    cached_client = MagicMock()
    conn._client = cached_client
    result = conn.get_client()
    mock_connect.assert_not_called()
    assert result is cached_client


def test_open_spreadsheet_delegates_to_client(conn) : 
    mock_client = MagicMock()
    conn._client = mock_client
    conn.open_spreadsheet("test_contacts")

    mock_client.open.assert_called_once_with("test_contacts")

def test_worksheet_returns_worksheets(conn ) : 
    mock_worksheet = MagicMock()
    mock_spreadsheet = MagicMock()
    mock_spreadsheet.get_worksheet.return_value = mock_worksheet
    mock_client = MagicMock()
    mock_client.open.return_value = mock_spreadsheet
    conn._client = mock_client

    result = conn.get_worksheet("test_contacts" , worksheet_index=0)
    mock_spreadsheet.get_worksheet.assert_called_once_with(0)
    assert result is mock_worksheet


def test_get_worksheet_raises_indexerror_when_index_missing(conn) : 
    mock_spreadsheet = MagicMock()
    mock_spreadsheet.get_worksheet.return_value = None
    mock_client =MagicMock()
    mock_client.open.return_value = mock_spreadsheet 
    conn._client = mock_client

    with pytest.raises(IndexError) : 
        conn.get_worksheet("test_contacts" , worksheet_index = 5)

def  test_get_worksheet_propagates_real_exceptions_unmodified(conn) : 
    mock_client =MagicMock()
    mock_client.open.side_effect = ValueError("Some underlying gspread error")
    conn._client = mock_client 
    with pytest.raises(ValueError , match="Some underlying gspread error"): 
        conn.get_worksheet("test_contacts")



