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
        try:
            with open('Spreadsheets.txt', 'r') as f:
                lines = f.readlines()
            for line in lines:
                self.tables.append(Table(line.split()[0], line.split()[1]))
            f.close()
        except:
            print('Spreadsheets.txt is not in directory')
            exit()

        creds = None
        if os.path.exists('token.json'):
            creds = Credentials.from_authorized_user_file('token.json', self.SCOPES)
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    'credentials.json', self.SCOPES)
                creds = flow.run_local_server(port=0)
            # Save the credentials for the next run
            with open('token.json', 'w') as token:
                token.write(creds.to_json())
        self.service = build('sheets', 'v4', credentials=creds)

    def check_postponement_counter(self, user_id):
        vkSrc = 'https://vk.com/id' + str(user_id)

        # Getting values of spreadsheet with counters
        values = self.service.spreadsheets().values().get(spreadsheetId=self.tables[1].id,
                                range=self.tables[1].range).execute().get('values', [])

        # Check postponement counter
        rowNum = -1

        if not values:
            return False
        else:
            for i in range(len(values)):
                if (values[i][1] == vkSrc):
                    rowNum = i
                    break
        if rowNum == -1 or int(values[rowNum][2]) < 10:
            return True
        return False

    def increase_postponement_counter(self, postponement):
        vkSrc = 'https://vk.com/id' + str(postponement.id)

        # Getting values of spreadsheet with counters
        values = self.service.spreadsheets().values().get(spreadsheetId=self.tables[1].id,
                                range=self.tables[1].range).execute().get('values', [])

        # Check postponement counter
        rowNum = -1

        if not values:
            return False
        else:
            for i in range(len(values)):
                if (values[i][1] == vkSrc):
                    rowNum = i
                    break

        if rowNum == -1:
            values = [
                [
                    postponement.fullname[0] + ' ' + postponement.fullname[1],
                    vkSrc,
                    '1'
                ]
            ]

            body = {
                'values': values
            }

            result = self.service.spreadsheets().values().append(
                spreadsheetId=self.tables[1].id, range=self.tables[1].range,
                valueInputOption='USER_ENTERED', body=body).execute()
            return

        values = [
            [
                values[rowNum][0],
                values[rowNum][1],
                str(int(values[rowNum][2]) + 1)
            ]
        ]

        body = {
            'values': values
        }

        result = self.service.spreadsheets().values().update(
            spreadsheetId=self.tables[1].id, range='A' + str(rowNum + 2) + ':C',
            valueInputOption='USER_ENTERED', body=body).execute()
        return

    def send_postponement_to_experts(self, postponement, hw):
        vkSrc = 'https://vk.com/id'+ str(postponement.id)

        values = [
            [
                datetime.datetime.now().strftime('%d.%m.%Y %H:%M:%S'),
                postponement.fullname[0] + ' ' + postponement.fullname[1],
                vkSrc,
                'ДЗ ' + str(postponement.hw),
                hw.deadline.strftime('%d.%m.%Y')
            ]
        ]

        body = {
            'values': values
        }

        result = self.service.spreadsheets().values().append(
            spreadsheetId=self.tables[0].id, range=self.tables[0].range,
            valueInputOption='USER_ENTERED', body=body).execute()
        return
