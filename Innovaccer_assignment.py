
# -----------------------Importing libraries------------------------------------#

import requests
from bs4 import BeautifulSoup
import re 
import bs4
import smtplib
from email.mime.text import MIMEText
import mysql.connector



Email_show_map = {}
shows_set = set()
status_dc = {}

#---------------------- Establishing connection with database---------------------#

mydb = mysql.connector.connect(
	host = "localhost",
	user = "root",
	password = "password123" 
	)
my_cursor = mydb.cursor()
my_cursor.execute("CREATE DATABASE testdb")
my_cursor.execute("USE testdb")

#---------------------------Main Function------------------------------------------#

def main():
    # creating first table containing email and show names 
    my_cursor.execute("CREATE TABLE users2 ( email TEXT , TVshow TEXT)")
    #  creating second table containing showname and their status 
    my_cursor.execute("CREATE TABLE showstats1 ( ShowName TEXT , status TEXT)")
    mydb.commit()
    
    n = int(input("Enter the number of entries : "))
    
    #storing the email id and fav tv shows into the table users2
    for i in range(n):
        _email = input("Email address: ")
        shows = input("TV Series: ")
        sqlStuff = "INSERT INTO users2 (email,TVshow) VALUES (%s, %s) "
        records = (_email,shows)
        my_cursor.execute(sqlStuff,records)
    mydb.commit()
    
    # Storing all uniques tv shows in shows_set.
    my_cursor.execute("SELECT * FROM users2  ")
    for _con in my_cursor:
    	 shows = _con[1].split(",")
    	 for _show in shows:
    		   shows_set.add(_show)
    
    # storing all the shows and their current status
    for _show in shows_set:
        _sqlStuff = "INSERT INTO showstats1 (ShowName,status) VALUES (%s, %s) "
        _status = FetchStatus(_show)
        _records = (_show,_status)
        my_cursor.execute(_sqlStuff,_records)
    mydb.commit()
    
    my_cursor.execute("SELECT * FROM users2")
    result1 = my_cursor.fetchall()
    for _row in result1:
        msg =""
        show_list = _row[1].split(",")
        for _shows in show_list:
            query = """SELECT status FROM showstats1 WHERE ShowName = '%s' """ %(_shows)
            my_cursor.execute(query)
            my_status = my_cursor.fetchone()
            temp = "\n\nTV Series name : " + _shows + "\nStatus : " + my_status[0]
            msg = msg + temp
        SendMail(_row[0],msg)
    
#-------------------Function for sending Email to users------------------------------------#

def SendMail(email,content):
    msg = MIMEText(content)
    mail= smtplib.SMTP('smtp.gmail.com',587)
    mail.ehlo()
    mail.starttls()
    mail.login('youremail@gmail.com','YourPassword')
    mail.sendmail('youremail@gmail.com',email,msg.as_string())
    mail.close()


#--------------------Function for fetching Show status from Imdb or Next-Episode------------#

def FetchStatus(name):
    status_list = ["Running","Upcoming Season Premiere","Canceled/Ended","Returning Series"]
    day_list = ["Mon","Tue","Wed","Thu","Fri","Sat","Sun"]

    sea_list = []
    for i in range(1,50):
        sea_list.append(str(i))
    
    n_link = name.lower()
    n_link = re.sub(r" ","-",name)
    sc = getHTML('https://next-episode.net/'+n_link)
    
    f1,f2,f3=0,0,0
    for div in sc.findAll('div'):
        # Iterate over the children of each matching div
        for c in div.children:
            # If it wasn't parsed as a tag, it may be a NavigableString
            if isinstance(c, bs4.element.NavigableString) :
                mystr = c.strip()
                mystr1 = mystr.split()
                
                if mystr == "Canceled/Ended" :
                    temp = "The show has finished streaming all it's episodes"
                    return temp
                    
                elif mystr == "Running" or mystr == "Upcoming Season Premiere" :
                    f1 = 1
                
                elif mystr == "Returning Series":
                    f2 = 1
            
                if len(mystr1)==4 and (mystr1[0] in day_list) and f1==1:
                        cd = clean_date(mystr1)
                        temp = "The next episode airs on " + cd 
                        return temp
                        
                if f2 == 1 and mystr in sea_list and len(mystr1)==1:
                    next_season = str(int(mystr) + 1)
                    imdb_link = GetLink(name,next_season)
                    air_year = FetchYear(imdb_link)
                    temp = "The next season begins in " + air_year 
                    if len(air_year.split()) == 1:
                        return temp
                    else :
                        return air_year


#--------------------------Function for getting the Beautiful soup object------------------------#

def getHTML(glink):
    page = requests.get(glink)
    return BeautifulSoup(page.content,'html.parser')

#--------------------------Function for getting Imdb link of the show----------------------------#

def GetLink(name,season):
    html = getHTML('https://www.google.co.in/search?q='+ name)
    for cite in html.findAll('cite'):
        if 'imdb.com/title/tt' in cite.text :
            html = getHTML(cite.text + 'episodes?season=' + season)
            return html
#-----------------------Function for cleaning date and converting in the required format---------#

def clean_date(date):
    date_map ={"Jan":'1',"Feb":'2',"Mar":'3',
               "Apr":'4',"May":'5',"Jun":'6',
               "Jul":'7',"Aug":'8',"Sep":'9',
               "Oct":'10',"Nov":'11',"Dec":'12'}
    date.pop(0)
    # ['May','16',2018]
    date[0] = date_map[date[0]]
    date[0],date[2]=date[2],date[0]
    date[1],date[2]=date[2],date[1]
    # ['2018', '5', '16,']
    date[2]=re.sub(r",","",date[2])
    new_str = "-".join(date)
    return new_str

#-----------------------Function for fetching the air year for returning series-------------------#

def FetchYear(soup):
    x=soup.findAll(class_="airdate")
    clean_x = x[0].text.strip()
    y = clean_x.split()
    if len(y) == 1 :
        return clean_x
    else :
        return "The show has finished streaming all it's episodes. "
        
if __name__ == '__main__':
    main()
