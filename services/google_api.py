import os

from googleapiclient.discovery import build
from google.oauth2 import service_account


class GoogleAdminSDKDirectoryAPI:

    def __init__(self, credentials_path):
        self.SCOPES = ['https://www.googleapis.com/auth/admin.directory.user.readonly',
                       'https://www.googleapis.com/auth/admin.directory.group.readonly',
                       'https://www.googleapis.com/auth/admin.directory.group.member.readonly',
                       ]

        self.SERVICE_ACCOUNT_FILE = credentials_path
        self.SUBJECT = "ron@test.authomize.com"

        self.credentials = service_account.Credentials.from_service_account_file(
            self.SERVICE_ACCOUNT_FILE, scopes=self.SCOPES, subject=self.SUBJECT)

        self.service = build('admin', 'directory_v1',
                             credentials=self.credentials)

    def get_all_users(self):
        results = self.service.users().list(customer='my_customer').execute()
        return results.get('users', [])

    def get_all_groups(self):
        results = self.service.groups().list(customer='my_customer').execute()
        return results.get('groups', [])

    def get_members_by_group(self, group_email):
        results = self.service.members().list(groupKey=group_email).execute()
        return results.get('members', [])
