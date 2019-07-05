from __future__ import print_function
import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import base64
import email
import datetime

import global_constants
from send_webhooks import SendWebhooks


# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/gmail.modify']


def main():
    creds = None
    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'notes/credentials.json', SCOPES)
            creds = flow.run_local_server()
        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    service = build('gmail', 'v1', credentials=creds)

    # Call the Gmail API to return all unread emails
    results = service.users().messages().list(userId='me', labelIds='UNREAD').execute()
    messages = results.get('messages', [])

    unread_new_turns = []

    for message in messages:
        # create a dictionary object representing the email
        msg = service.users().messages().get(userId='me', id=message['id'], format='raw').execute()

        # retrieve raw byte data from dictionary object
        msg_bytes = base64.urlsafe_b64decode(msg['raw'].encode('ASCII'))

        # create message object from byte data
        mime_msg = email.message_from_bytes(msg_bytes)

        # if the subject of the message is not the expected subject, do not pull data from it
        if not mime_msg['Subject'] == global_constants.subject:
            break

        # iterate over parts of the email object and store only the plain text of the email
        if not mime_msg.is_multipart():
            # retrieve text of email part
            text = mime_msg.get_payload()

            # store dictionary returned from pull_data in unread_new_turns
            new_turn = pull_data(text)
            unread_new_turns.append(new_turn)

            # mark processed email as read
            mark_as_read(service, message['id'])
        else:
            for part in mime_msg.walk():
                content_type = part.get_content_type()
                content_disposition = str(part.get('Content-Disposition'))

                # do not pull data from email part if it is not plain text with no attachments
                if content_type == 'text/plain' and 'attachment' not in content_disposition:
                    # retrieve text of email part
                    text = part.get_payload()

                    # store dictionary returned from pull_data in unread_new_turns
                    new_turn = pull_data(text)
                    unread_new_turns.append(new_turn)

                    # mark processed email as read
                    mark_as_read(service, message['id'])
                    break

    if unread_new_turns:
        # create SendWebhook object and pass it all extracted data
        sender = SendWebhooks(unread_new_turns)

        # initiate send_all_new_turns and store tuple in sender_data
        # sender data in the format: ((int)webhooks sent, (int)total webhooks)
        turns_sent = sender.send_all_new_turns()

        print("%s out of %s webhooks were sent at %s." % (turns_sent, len(sender.new_turns), datetime.datetime.now()))

        if not turns_sent == len(sender.new_turns):
            print("new turn that caused the error:")
            print(sender.new_turns[turns_sent])
        print("------------")
    else:
        print("No new turns to send at %s." % datetime.datetime.now())
        print("------------")


# returns dictionary data after given fields
# formatted as {string_key.when:email_time,
#               string_key.game:game_name,
#               string_key.player:player_name,
#               string_key.turn:turn_number}
def pull_data(email_text):
    fields_to_find = [global_constants.when, global_constants.game, global_constants.player, global_constants.turn]
    found_data = {}
    i = 0
    for field in fields_to_find:
        # find index of the field starting at last point in the email string
        # raise an error if the field is not found
        try:
            i = email_text.index(field, i)
        except ValueError:
            raise ValueError("Field not found within string after given starting point")

        # set index to the first character after the field
        i = i + len(field)

        # store the string after the field and store it within found_data with the field as the key
        data = ""
        while not email_text[i] == '\r':
            data += email_text[i]
            i += 1
        found_data[field] = data

    # raise an error if found_data is not the same size as fields_to_find
    assert (len(found_data) == len(fields_to_find))
    return found_data


# mark email with passed id as read
def mark_as_read(service, msg_id):
    editing_labels = {'addLabelIds': [], 'removeLabelIds': ['UNREAD']}
    service.users().messages().modify(userId='me', id=msg_id, body=editing_labels).execute()


if __name__ == '__main__':
    main()
