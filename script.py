import requests 
from bs4 import BeautifulSoup 
from PIL import Image
import requests
from io import BytesIO
from datetime import date, timedelta


dateRaw = open('date.txt','r').read()
print(dateRaw)
date = date.fromisoformat(dateRaw.replace('/','-'))
print(date)



def getdata(url): 
	r = requests.get(url) 
	return r.text 
	
formattedDate = dateRaw.replace('-','/')
htmldata = getdata(f'https://www.gocomics.com/calvinandhobbes/{formattedDate}') 
soup = BeautifulSoup(htmldata, 'html.parser') 

imageList = soup.find_all('img')

print(len(imageList))

for image in imageList:
    print(image['src'])

url = imageList[4]['src']



response = requests.get(url)
img = Image.open(BytesIO(response.content))
img.show(BytesIO(response.content))

# update date for tomorrow's strip
date += timedelta(days=1)
file = open('date.txt', 'w')
dateRaw = str(date)
file.write(dateRaw)

