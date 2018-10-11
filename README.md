## TV-Show-Reminder
A Python script asks multiple users for their email address and their favourite TV show,Stores them into the MySql Database table,fetches the status of TV shows from websites such as [Imdb](https://www.imdb.com) and [Next Episode](https:www.next-episode.net) and sends a single Email to each user consisting of their TV favourite shows'  and their AIR status.
## Dependencies :
```
Python-3.6.5
BeautifulSoup4 
requests
smtplib
mysql.connector
re
```
## Example use case :
Input :
```
Enter the number of entries : 3
Email address: abc@gmail.com
TV Series: gotham,game of thrones,sherlock,suits
Email address: mus@gmail.com
TV Series: pitchers,the vampire diaries,sherlock
Email address: xyz@gmail.com
TV Series: breaking bad,gotham,the flash
```
Output :
The Email sent to abc@gmail.com looks like :
```
TV Series name : gotham
Status : The next episode airs on 2018-5-17

TV Series name : game of thrones
Status : The next season begins in 2019

TV Series name : sherlock
Status : The show has finished streaming all it's episodes. 

TV Series name : suits
Status : The show has finished streaming all it's episodes. 
```