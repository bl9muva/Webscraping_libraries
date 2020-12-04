"""
Web Scraper
Binyong Liang
"""

import re
import requests
from bs4 import BeautifulSoup
from datetime import datetime
import pandas as pd


#function to get a block of data by web scraping
def scraping_info(url):
    response = requests.get(url)
    html = response.content
    soup = BeautifulSoup(html, 'lxml')
    
    name = soup.find('title').text         #name of library
    
    info = soup.find('dd').text             #find the open hours, phone and fax
    hourinfo = re.split("\n|\t|\|", info)   #split string into a list
    for item in hourinfo:               #cleanup the hourinfo list 
        if "weekend" in item:
            hourinfo.remove(item)
    info = [name, hourinfo]
    return info        

#define a function to return a list with two float numbers 
#for openning and closing hours
def hour_range(item):          
    Todaytime=[]
    for s in re.findall(r'\d+', item):
        Todaytime.append(float(s))          #may not be all integers
    if len(Todaytime) >= 3:                     #dealing with open at half hour
        Todaytime[0]=Todaytime[0] + Todaytime[1]/60    #convert minutes to hours
        Todaytime.remove(Todaytime[1])    
    if len(Todaytime) > 0:  
        if Todaytime[0] <= 7:                   #library may only open in the pm
            Todaytime[0] += 12
        Todaytime[len(Todaytime)-1] += 12         #convert to 24 hour format  
    return Todaytime

#extract hours from the info scraped from web 
#for unspecified weekdays, inherit values from the previous day    
def getweeklytime(hourinfo):
    for item in hourinfo:                  
        if "Monday" in item:
            Montime = hour_range(item)
            Tuestime=Montime
            Wedtime=Montime
            Thurstime=Montime
            Fritime=Montime
            Sattime=Montime
            Suntime=Montime
        elif "Tuesday" in item:
            Tuestime = hour_range(item)
            Wedtime=Tuestime
            Thurstime=Tuestime
            Fritime=Tuestime
            Sattime=Tuestime
            Suntime=Tuestime        
        elif "Wednesday" in item:
            Wedtime = hour_range(item)
            Thurstime=Wedtime
            Fritime=Wedtime
            Sattime=Wedtime
            Suntime=Wedtime 
        elif "Thursday" in item:
            Thurstime = hour_range(item)
            Fritime=Thurstime
            Sattime=Thurstime
            Suntime=Thurstime         
        elif "Friday" in item:
            Fritime = hour_range(item)
            Sattime=Fritime
            Suntime=Fritime  
        elif "Saturday" in item:
            Sattime = hour_range(item)
            Suntime=Sattime
        elif "Sunday" in item:
            Suntime = hour_range(item)
    weeklytime = [Montime, Tuestime, Wedtime, Thurstime, Fritime,
                  Sattime, Suntime]
    return weeklytime

#this is a list of area libraries
librarylist = ['https://www.jmrl.org/br-central.htm',
               'https://www.jmrl.org/br-crozet.htm',
               'https://www.jmrl.org/br-gordon.htm',
               'https://www.jmrl.org/br-greene.htm',
               'https://www.jmrl.org/br-louisa.htm',
               'https://www.jmrl.org/br-nelson.htm',
               'https://www.jmrl.org/br-northside.htm',
               'https://www.jmrl.org/br-scottsville.htm']

#prepare an output csv file, this is the header (first row)
header = ['', 'Monday-o', 'Monday-c', 'Tuesday-o','Tuesday-c', 'Wednesday-o',
          'Wednesday-c','Thursday-o','Thursday-c','Friday-o','Friday-c',
          'Saturday-o','Saturday-c','Sunday-o', 'Sunday-c']
open('libraryhour.csv', 'w').close()    #To initialize the output file
for hd in header:
    with open('libraryhour.csv', 'a') as f:
        f.write("%s,"%hd)
    f.close()
#call scraping_info function recursively
for lib in librarylist:
    scraped = scraping_info(lib)
    name = scraped[0]
    hourinfo = scraped[1]
    with open('libraryhour.csv', 'a') as f:
        f.write("\n%s,"%name)
        for item in getweeklytime(hourinfo):
            for j in item:
                f.write("%2.1f,"%j)
    f.close()

#this is to use our web-scraped data
#This program takes the current time, and will tell the user
#the list of libraries that are current open
df = pd.read_csv('libraryhour.csv')         #from csv to panda dataframe
now = datetime.now()
hour24=float(now.strftime('%H')) + float(now.strftime('%M'))/60  
weekday=datetime.today().weekday()          #take weekday and hours
openlist=[]
for i in range(0, len(df)):
    if (hour24 >= df.iat[i,2*weekday+1] and hour24 < df.iat[i,2*weekday+2]):
        openlist.append(df.iat[i,0])
if openlist == []:
    print("All libraries are closed, please wait for another day!")
else:
    print("The following libraries are open at this moment:")
    print(openlist)





       
        