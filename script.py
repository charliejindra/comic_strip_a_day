import requests 
from bs4 import BeautifulSoup 
from PIL import Image
import requests
from io import BytesIO
from datetime import date, timedelta, datetime
import os
import base64
from email.mime.text import MIMEText
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from time import sleep
import json

# If modifying these SCOPES, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/gmail.send']

def getdata(url): 
	r = requests.get(url) 
	return r.text 

def create_message(sender, to_list, subject, message_text):
    """Create a message for an email."""
    message = MIMEText(message_text, 'html')
    message['to'] = ', '.join(to_list)
    message['from'] = sender
    message['subject'] = subject
    raw = base64.urlsafe_b64encode(message.as_bytes())
    raw = raw.decode()
    return {'raw': raw}

def send_message(service, user_id, message):
    """Send an email message."""
    try:
        message = service.users().messages().send(userId=user_id, body=message).execute()
        print(f'Message Id: {message["id"]}')
        return message
    except Exception as error:
        print(f'An error occurred: {error}')
        return None


while True:
	time = datetime.now()
	# run every morning at 5am
	# while (time.hour != 5) or (time.minute != 0) or (time.second > 5):
	# 	print(time.hour, time.minute, time.second)
	# 	sleep(1)
	# 	time = datetime.now()

	# WEB SCRAPING
	# get the date of the next comic to send
	dateRaw = open('date.txt','r').read()
	print(dateRaw)
	date = date.fromisoformat(dateRaw.replace('/','-'))
	print(date)

	# scrape gocomics
	formattedDate = dateRaw.replace('-','/')
	htmldata = getdata(f'https://www.gocomics.com/calvinandhobbes/{formattedDate}') 
	soup = BeautifulSoup(htmldata, 'html.parser') 

	imageList = soup.find_all('img')

	print(len(imageList))

	for image in imageList:
		print(image['src'])

	# so far this seems to be the index that the comic always is. stay tuned
	# ok its not now lol as of 2-28-1986. hopefully itll be easy to figure out a way to get it
	url = imageList[4]['src']


	"""Shows basic usage of the Gmail API.
	Sends an email.
	"""
	creds = None
	# The file token.json stores the user's access and refresh tokens, and is
	# created automatically when the authorization flow completes for the first
	# time.
	if os.path.exists('token.json'):
		creds = Credentials.from_authorized_user_file('token.json', SCOPES)
	# If there are no (valid) credentials available, let the user log in.
	if not creds or not creds.valid:
		if creds and creds.expired and creds.refresh_token:
			print('went to refresh token flow')
			creds.refresh(Request())
		else:
			flow = InstalledAppFlow.from_client_secrets_file(
				'credentials.json', SCOPES)
			creds = flow.run_local_server(port=0)
		# Save the credentials for the next run
		with open('token.json', 'w') as token:
			token.write(creds.to_json())

	service = build('gmail', 'v1', credentials=creds)

	# Create the email content
	# sender -> recipient
	currentDate = datetime.today().strftime('%m-%d-%Y')
	formatOldDate = date.strftime('%m-%d-%Y')
	msgBody =f"""
	<html>
		<div style="align: center">
			<h2>Calvin And Hobbes {currentDate}</h2>
			<h3>Original run date - {formatOldDate}</h3>
			<img src='{url}'>
		</div>
	</html>
	"""
	

	# Example usage
	file_path = "email_list.json"
	with open(file_path, 'r', encoding='utf-8') as file:
		data = json.load(file)

	# recipients = data.get("recipients", [])
	# TO TEST UNCOMMENT THE LINE BELOW AND COMMENT THE LINE ABOVE
	recipients = data.get("test_recipients", [])
	print(recipients)


	message = create_message("charlessjindra@gmail.com", recipients, f"Calvin and Hobbes {currentDate}", msgBody)
	send_message(service, "me", message)

	# update date for tomorrow's strip
	date += timedelta(days=1)
	file = open('date.txt', 'w')
	dateRaw = str(date)
	file.write(dateRaw)

	print("now waiting a while")
	sleep(1000)