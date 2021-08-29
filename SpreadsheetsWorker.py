from __future__ import print_function
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from Delay import *
import datetime
from Homework import homework

class Table:
    def __init__(self, id, range):
        self.id = id
        self.range = range

class SpreadsheetsWorker:

    def __init__(self):
        # If modifying these scopes, delete the file token.json.
        self.SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

        # The ID and range of a needed spreadsheets.
        self.tables = []
        with open(os.path.realpath(__file__)[:os.path.realpath(__file__).rfind("\\") + 1] + 'Spreadsheets.txt', 'r') as f:
            lines = f.readlines()
        for line in lines:
            self.tables.append(Table(line.split()[0], line.split()[1]))

        creds = None
        if os.path.exists(os.path.realpath(__file__)[:os.path.realpath(__file__).rfind("\\") + 1] + 'token.json'):
            creds = Credentials.from_authorized_user_file(os.path.realpath(__file__)[:os.path.realpath(__file__).rfind("\\") + 1] + 'token.json', self.SCOPES)
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    os.path.realpath(__file__)[:os.path.realpath(__file__).rfind("\\") + 1] + 'credentials.json', self.SCOPES)
                creds = flow.run_local_server(port=0)
            # Save the credentials for the next run
            with open(os.path.realpath(__file__)[:os.path.realpath(__file__).rfind("\\") + 1] + 'token.json', 'w') as token:
                token.write(creds.to_json())
        self.service = build('sheets', 'v4', credentials=creds)

    def send_postponement_count(self, postponementsCount):
        body = {
            'values': postponementsCount
        }

        result = self.service.spreadsheets().values().update(
            spreadsheetId=self.tables[1].id, range=self.tables[1].range,
            valueInputOption='USER_ENTERED', body=body).execute()
        return

    def send_postponement_to_experts(self, postponements):
        for p in postponements:
            p[4] = p[4].split()[0]
        body = {
            'values': postponements
        }

        result = self.service.spreadsheets().values().append(
            spreadsheetId=self.tables[0].id, range=self.tables[0].range,
            valueInputOption='USER_ENTERED', body=body).execute()
        return
