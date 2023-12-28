# your_app/import_google_sheets.py

import sqlite3
from sqlite3 import Error
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from .models import Application
from django.db import IntegrityError

def get_from_sheet(sheet_name, credentials_config):
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds_obj = ServiceAccountCredentials.from_json_keyfile_dict(credentials_config, scope)
    client = gspread.authorize(creds_obj)
    sheet = client.open(sheet_name).sheet1
    return sheet.get_all_values()

class SQLite:
    DB_NAME = "db.sqlite"

    def __init__(self):
        self.conn = self.create_connection()
        self._get_or_create_table()

    @classmethod
    def create_connection(cls):
        conn = None
        try:
            conn = sqlite3.connect(cls.DB_NAME)
            return conn
        except Error as e:
            print(e)

    def _get_or_create_table(self):
        create_table_sql = """CREATE TABLE IF NOT EXISTS details (
            timestamp varchar(25) PRIMARY KEY,
            name varchar(30) NOT NULL,
            phone_number varchar(20) NOT NULL,
            email varchar(50) NOT NULL,
            age varchar(25) NOT NULL,
        )"""
        try:
            c = self.conn.cursor()
            c.execute(create_table_sql)
        except Error as e:
            print(e)

    def add_data_to_table(self, rows):
        for row in rows[1:]:
            try:
                Application.objects.create(
                    timestamp=row[0],
                    name=row[1],
                    phone_number=row[2],
                    email=row[3],
                    age=row[4],
                )
            except IntegrityError as e:
                # Handle duplicate entries if needed
                print(f"Error adding row: {row}")
                print(e)
                pass

# Include the credentials information here
config = {
    "type": "service_account",
    "project_id": "aggerman-sheets",
    "private_key_id": "f393f9ef2934e9d3a8e4c95fc063ce74784bfce1",
    "private_key": "-----BEGIN PRIVATE KEY-----\nMIIEvAIBADANBgkqhkiG9w0BAQEFAASCBKYwggSiAgEAAoIBAQDjFe9roGzAdF5w\nc0dIJlR+8RcqZ/B96GHAZRG1bLtn04j+oG6kx8P5yDE3UOoAQIBCZ81bywX/c30N\nAmv0y17R8YxlxmzOSRB+7ov7fWW3WSQRGkfMOR6MKu+b3q+U3XMv4iZz93ntIfQz\nw4yeKgy2cCmlijEqNw+cUj+CLzgXNPxKAbAlBfsnLjR4/0ynT+hIYptBIljD1tO0\n8MiI4Ykb8ON2M1WfejYA9usxEvdN7+o38s1RN+gPkIKIHreBSTu1q89le2HXZG7c\n6AuHNV6Ib2s/0Jjszuaxw3I67M7DPEF+iZcOQvlSm/L1Bl+OWbJl+Ri5lvI78J5s\nRNiYHj6JAgMBAAECggEABi0mDmjWHGPt36QbB7jXKn63MRWTonEMG5YEJcmXzUqh\nGr/VUpEGYQhTYlxGiQw4ENZO7RS4DIshFxX+RrGzWgV2WpxLgE7XboRhdU0jU5nO\nk9KBqmnRTWGrk7M6VlOxmtdNUXElNVBrmm7Sp8igAORLFbANB0dpGsjX5lwPa/4d\nUpawCQSxOkq2JCflObXtk1RkK5uKDGaqW9hgbw4dNFPvL4+dU35dBbfu4CgsSXxY\noKO7YxWyEYLRxnza8A36P78hdwAWfDriiGdkhow8oJnfO82Fj/eVW9sB6UPOwSe1\nRGe7nNBGz6020bcXRUM94O05VlxVCKTX2tuT8GCqewKBgQD0cI2s8hEM7TvI/w1l\nWbWcJpE9U+rdc6t06hCZrd5mRI2E/bcNZdhOE4wlASmHLMHYVfBLRPlVB3Nor3v8\nXhG4Vd+lXpYK55Ei5ZrX3jkO/FzEiiwP0Xnh6ZkrO+R5ro+7eTjJlU4Zduwr6a3R\ntME0YCpwJfjIszPNjeIuoQDOCwKBgQDt00au3Yr6AV63wb+51SgUXwEMWfpHHczn\nX0WJodhfUCbCksvc7TM+4G0O/SK/9W3R+YL4jzZwGkwqrWNDKEFzeOBP7GQDYIND\nc3hw7ASLLBBghtu0VmkBs+8j16ZPV2PdG+9/n+SgrDeRxaHNNO9u2MSjnBEk3rX+\ngrHTsV+GOwKBgCgj24AM+DPROUIWcBK2mpYb1znk7+qRthQq47L41E6i70Jpj4fJ\ns62OlDL3b+RcuzBVXHJfzznhUVhdiNS2dd55a5JyZ90+jZzXa4gLW/9T/b/gmL+4\nPHWWsKpi2XAJ9Fxq2aJwvDR+TOYhJ4QKVLfPGujzs1jx5I3awMu7cLBlAoGARQvo\n4o3ZcnoBWNI8aqRzDW8Dq+VXn1wMiEQFuU6utgVcK3NZEpwfG6smnoppk1ea+bI6\nDxXtFSDdaiqKvg2q6u52GV4lL0HO+j9FAWvUad9yJcQhdzr7I45s6HgMhc52ZNRe\ndSwjwW4eeAjrz9sFhKYUePevloe+SNUC8dX2SM8CgYACqtd9nWbzRLncAjOi01lj\nre3hYKFhED2KboGOyuN44XV+cfLUANRYPNsKXgFIJUGhRK27KuDOAk4wMD8eAIdr\nesxP8VKiRP9MucKemgbNE1Jut5RJjieTT/61xqyE0TvDRst+MVL8ep+OEhsK/FKZ\n8QkXCXQoQvWTHTZoW3WoTA==\n-----END PRIVATE KEY-----\n",
    "client_email": "service-account@aggerman-sheets.iam.gserviceaccount.com",
    "client_id": "101007819498863171311",
    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
    "token_uri": "https://oauth2.googleapis.com/token",
    "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
    "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/service-account%40aggerman-sheets.iam.gserviceaccount.com",
    "universe_domain": "googleapis.com"
}

# Use the get_from_sheet and SQLite classes as needed with the config
if __name__ == '__main__':
    # Fetches data from the sheets
    data = get_from_sheet("Website", config)

    # Initialize SQLite class and add data to the SQLite table
    sqlite_util = SQLite()
    sqlite_util.add_data_to_table(data)

