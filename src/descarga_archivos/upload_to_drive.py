#!/usr/bin/env python3
import os
import json
import sys
from pydrive2.auth import GoogleAuth
from pydrive2.drive import GoogleDrive

# Service account JSON stored as a GitHub secret
SERVICE_ACCOUNT_KEY = os.getenv("GDRIVE_SERVICE_ACCOUNT")
# Your target folder in Google Drive
FOLDER_ID = "1-3HZvmWiR2O83XHf7oGC3Wq4S0Ql_WGt"

def authenticate() -> GoogleDrive:
    key_dict = json.loads(SERVICE_ACCOUNT_KEY)
    gauth = GoogleAuth()
    gauth.settings["service_config"] = {
        "client_json": key_dict,
        "service": "drive",
        "service_account_email": key_dict["client_email"]
    }
    gauth.ServiceAuth()
    return GoogleDrive(gauth)

def upload_file(filepath: str) -> None:
    drive = authenticate()
    file_name = os.path.basename(filepath)
    gfile = drive.CreateFile({
        "title": file_name,
        "parents": [{"id": FOLDER_ID}]
    })
    gfile.SetContentFile(filepath)
    gfile.Upload()
    print(f"Uploaded {file_name} to Drive folder {FOLDER_ID}")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python upload_to_drive.py <path-to-xlsx>")
        sys.exit(1)
    upload_file(sys.argv[1])
