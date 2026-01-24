import os

import httplib2
from googleapiclient.discovery import Resource, build
from oauth2client.service_account import ServiceAccountCredentials

# if modifying these scopes, delete the file token.json
# retrieve https://developers.google.com/calendar/api/auth

SCOPES = ["https://www.googleapis.com/auth/calendar"]
SERVICE_ACCOUNT_KEY_FILE = "./secrets/service-credentials.json"
_SERVICE = None

def get_oauth2_creds() -> ServiceAccountCredentials:
    creds = None

    if os.path.exists(SERVICE_ACCOUNT_KEY_FILE):
        creds = ServiceAccountCredentials.from_json_keyfile_name(
            filename=SERVICE_ACCOUNT_KEY_FILE,
            scopes=SCOPES,
        )
    
    return creds

def get_service() -> Resource:
    global _SERVICE
    if _SERVICE:
        return _SERVICE
    creds = get_oauth2_creds()
    if not creds:
        raise FileNotFoundError(
            f"Missing service account credentials at {SERVICE_ACCOUNT_KEY_FILE}. "
            "Add the file and retry."
        )
    http_auth = creds.authorize(httplib2.Http())
    _SERVICE = build("calendar", "v3", http=http_auth)
    return _SERVICE
