import os.path
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError


class GmailConnector:
    def __init__(self):
        self.SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]
        self.creds = None
        self.service = None

    def authenticate(self):
        if os.path.exists('token.json'):
            self.creds = Credentials.from_authorized_user_file('token.json', self.SCOPES)
        if not self.creds or not self.creds.valid:
            if self.creds and self.creds.expired and self.creds.refresh_token:
                self.creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file('credentials.json', self.SCOPES)
                self.creds = flow.run_local_server(port=0)
            with open('token.json', 'w') as token:
                token.write(self.creds.to_json())

    def build_service(self):
        try:
            self.service = build('gmail', 'v1', credentials=self.creds)
        except HttpError as error:
            print(f'An error occurred: {error}')

    def list_labels(self):
        try:
            results = self.service.users().labels().list(userId='me').execute()
            labels = results.get('labels', [])
            return labels
        except Exception as e:
            print(f'An error occurred: {e}')
            return []

    def get_all_emails(self, query=''):
        """
        Retrieves all emails matching the given query.
        :param query: String to filter the messages returned. (Default: empty string)
        :return: List of email messages.
        """
        try:
            response = self.service.users().messages().list(userId='me', q=query).execute()
            messages = response.get('messages', [])

            all_messages = []
            while 'nextPageToken' in response:
                page_token = response['nextPageToken']
                response = self.service.users().messages().list(userId='me', q=query, pageToken=page_token).execute()
                messages.extend(response.get('messages', []))

            for message in messages:
                msg = self.service.users().messages().get(userId='me', id=message['id']).execute()
                all_messages.append(msg)

            return all_messages
        except Exception as e:
            print(f'An error occurred: {e}')
            return []

    def get_emails_by_label(self, label_ids):
        """
        Retrieves all emails with the specified label(s).
        :param label_ids: List of label IDs to filter the messages.
        :return: List of email messages.
        """
        try:
            response = self.service.users().messages().list(userId='me', labelIds=label_ids).execute()
            messages = response.get('messages', [])

            all_messages = []
            while 'nextPageToken' in response:
                page_token = response['nextPageToken']
                response = self.service.users().messages().list(userId='me', labelIds=label_ids, pageToken=page_token).execute()
                messages.extend(response.get('messages', []))

            for message in messages:
                msg = self.service.users().messages().get(userId='me', id=message['id']).execute()
                all_messages.append(msg)

            return all_messages
        except Exception as e:
            print(f'An error occurred: {e}')
            return []

    def get_senders_by_label(self, label_ids):
        """
        Retrieves all emails with the specified label(s) and compiles a list of senders.
        :param label_ids: List of label IDs to filter the messages.
        :return: List of senders' email addresses.
        """
        try:
            response = self.service.users().messages().list(userId='me', labelIds=label_ids).execute()
            messages = response.get('messages', [])

            senders = set()
            while 'nextPageToken' in response:
                page_token = response['nextPageToken']
                response = self.service.users().messages().list(userId='me', labelIds=label_ids, pageToken=page_token).execute()
                messages.extend(response.get('messages', []))

            for message in messages:
                msg = self.service.users().messages().get(userId='me', id=message['id'], format='metadata').execute()
                headers = msg.get('payload', {}).get('headers', [])
                sender = next((header['value'] for header in headers if header['name'] == 'From'), None)
                if sender:
                    senders.add(sender)

            return list(senders)
        except Exception as e:
            print(f'An error occurred: {e}')
            return []

    def find_label_id_by_name(self, label_name):
        """
        Finds the label ID for a given label name.
        :param label_name: The name of the label.
        :return: The ID of the label or None if not found.
        """
        try:
            response = self.service.users().labels().list(userId='me').execute()
            labels = response.get('labels', [])

            for label in labels:
                if label['name'].lower() == label_name.lower():
                    return label['id']

            return None
        except Exception as e:
            print(f'An error occurred: {e}')
            return None



# Example usage
if __name__ == '__main__':
    connector = GmailConnector()
    connector.authenticate()
    connector.build_service()
    label_id_promotion = 'CATEGORY_PROMOTIONS'
    label_id_updates = 'CATEGORY_UPDATES'
    label_id_forums = 'CATEGORY_FORUMS'
    label_id = 'YOUR_LABEL_ID'
    senders = connector.get_senders_by_label([label_id_promotion])
    print(f"Senders in label ID {label_id}: {senders}")
