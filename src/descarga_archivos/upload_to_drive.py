#!/usr/bin/env python3
import os
import sys
import json
import tempfile
from pydrive2.auth import GoogleAuth
from pydrive2.drive import GoogleDrive

def authenticate() -> GoogleDrive:
    sa_key = os.getenv("GDRIVE_SERVICE_ACCOUNT")
    if not sa_key:
        raise RuntimeError("GDRIVE_SERVICE_ACCOUNT not set")

    key_dict = json.loads(sa_key)
    with tempfile.NamedTemporaryFile(
        mode="w+", suffix=".json", delete=False
    ) as f:
        json.dump(key_dict, f)
        sa_path = f.name

    gauth = GoogleAuth()
    gauth.settings["service_config"] = {
        "client_json":    key_dict,
        "service":        "drive",
        "service_account_email": key_dict["client_email"],
    }
    gauth.ServiceAuth()
    return GoogleDrive(gauth)

def upload_file(filepath: str) -> None:
    folder_id = os.getenv("GDRIVE_FOLDER_ID")
    if not folder_id:
        raise RuntimeError("GDRIVE_FOLDER_ID not set")

    drive = authenticate()
    file_name = os.path.basename(filepath)

    gfile = drive.CreateFile({
        "title":   file_name,
        "parents": [{"id": folder_id}],
    })
    gfile.SetContentFile(filepath)
    gfile.Upload()
    print(f"✅ Uploaded {file_name} to Drive folder {folder_id}")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python upload_to_drive.py <path-to-file>")
        sys.exit(1)
    upload_file(sys.argv[1])
