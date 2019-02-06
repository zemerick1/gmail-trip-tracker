from __future__ import print_function
from flask import Flask
from flask import Markup
from flask import Flask
from flask import render_template
import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from bs4 import BeautifulSoup
import base64
import re

# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

"""
Searches GMAIL for location services emails and pulls the cities traveled count out then plots the data by Month.
    Thanks to: https://github.com/abhishekchhibber/Gmail-Api-through-Python
"""
creds = None
# The file token.pickle stores the user's access and refresh tokens, and is
# created automatically when the authorization flow completes for the first
# time.
if os.path.exists('token.pickle'):
    with open('token.pickle', 'rb') as token:
        creds = pickle.load(token)
# If there are no (valid) credentials available, let the user log in.
# This will open a browser to store the token locally.
if not creds or not creds.valid:
    if creds and creds.expired and creds.refresh_token:
        creds.refresh(Request())
    else:
        flow = InstalledAppFlow.from_client_secrets_file(
            'credentials.json', SCOPES)
        creds = flow.run_local_server()
    # Save the credentials for the next run
    with open('token.pickle', 'wb') as token:
        pickle.dump(creds, token)
user_id = 'me'
service = build('gmail', 'v1', credentials=creds)

# Call the Gmail API
query = 'noreply-maps-timeline@google.com'
results = service.users().messages().list(userId=user_id,q=query).execute()
messages = results['messages']
# Ugly but works perfectly for these emails.
regMonth = r'(Jan(uary)?|Feb(ruary)?|Mar(ch)?|Apr(il)?|May|Jun(e)?|Jul(y)?|Aug(ust)?|Sep(tember)?|Oct(ober)?|Nov(ember)?|Dec(ember)?)'
regYear = r'(\d{4})'
# Initialize data that will be fed to our line chart.
city_data = []
month_data = []
for msg in messages:
    msg_id = msg['id']
    message = service.users().messages().get(userId=user_id, id=msg_id).execute()  # fetch the message using API
    payld = message['payload']  # get payload of the message base64 encoded
    headr = payld['headers']  # get header of the payload

    for one in headr:  # getting the Subject
        if one['name'] == 'Subject':
            msg_subject = one['value']
            line_reg = re.findall(regMonth, msg_subject)
            for match in line_reg:
                if match is None:
                    continue
                else:
                    for two in headr:  # getting the date
                        if two['name'] == 'Date':
                            msg_date = two['value']
                            year_reg = re.findall(regYear, msg_date)
                    # Add month + year
                    month_data.append(match[0] + ' ' + year_reg[0])
    # Fetching message body
    mssg_parts = payld['parts']  # fetching the message parts
    part_one = mssg_parts[0]  # fetching first element of the part
    part_body = part_one['body']  # fetching body of the message
    part_data = part_body['data']  # fetching data from the body
    clean_one = part_data.replace("-", "+")  # decoding from Base64 to UTF-8
    clean_one = clean_one.replace("_", "/")  # decoding from Base64 to UTF-8
    clean_two = base64.b64decode(bytes(clean_one, 'UTF-8'))  # decoding from Base64 to UTF-8
    soup = BeautifulSoup(clean_two, "lxml")
    mssg_body = soup.prettify().splitlines()
    # mssg_body is a readable form of message body
    # Read msg to find the line we want.
    for lines in mssg_body:
        if 'cities visited this month' in lines:
            cities_visited = lines.strip().split(' ')[0]
            city_data.append(cities_visited)

# Build Flask App to serve the data nicely.
app = Flask(__name__)

@app.route("/")
def chart():
    labels = month_data
    values = city_data
    return render_template('chart.html', title='Cities Traveled', max=50, values=values, labels=labels)

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5004, debug=True)