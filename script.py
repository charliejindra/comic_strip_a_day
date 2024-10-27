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

# If modifying these SCOPES, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/gmail.send']

def getdata(url): 
	r = requests.get(url) 
	return r.text 

def create_message(sender, to, subject, message_text):
    """Create a message for an email."""
    message = MIMEText(message_text, 'html')
    message['to'] = to
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
url = imageList[4]['src']

# can i tear this out? show the image on screen.
# i should just need the URL
response = requests.get(url)
img = Image.open(BytesIO(response.content))
img.show(BytesIO(response.content))

# update date for tomorrow's strip
date += timedelta(days=1)
file = open('date.txt', 'w')
dateRaw = str(date)
file.write(dateRaw)

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
currentDate = datetime.today().strftime('%Y-%m-%d')
msgBody =f"""
<html>
	<h2>Calvin And Hobbes {currentDate}</h2>
	<h3>Original run date - {date}</h3>
	<img src='{url}'>
</html>
"""

message = create_message("charlessjindra@gmail.com", "charlessjindra@gmail.com", "Subject Here", msgBody)
send_message(service, "me", message)
