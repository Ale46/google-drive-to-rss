##Google Drive to Rss [![gittip](https://img.shields.io/gittip/Ale46.svg)](https://www.gratipay.com/Ale46/)
A tool that give you the possibility to have a rss feed from a **public** [google drive](http:/drive.google.com) directory. Useful in combination with [Pushbullet](pushbullet.com) , [IFFT](ifttt.com) or just an helper to setup a personal podcast based on google drive.

##Configuration
###options.conf
```ini
[Options]
rss_url=http://example.com/rss/
server_port=5000 #only used if you run locally
```
###rss.conf
```ini
[RSS_ROUTE_NAME] #in this case you can access the feed at http://example.com/rss/RSS_ROUTE_NAME
rss_title: Rss title
rss_desc: Rss description
drive_link: https://drive.google.com/folderview?id=FOLDER_ID
feed_entry_prepend: optional text to prepend to title
feed_entry_postpend: optional text to postpend to title
check: 120 #define the minutes between each check
max_item: 10 #max items shown by rss feed
```
You can define as many sections you want
##Run locally
* Clone the repository
```bash
git clone https://github.com/Ale46/google-drive-to-rss.git
```
* Install dependecies
```bash
(sudo) pip install -r requirements.txt
```
* Edit local.conf.example
```ini
[Database]
hostname: localhost
username: your_username
password: db_password
database: database_name
```
* Rename it
```bash
mv local.conf.example local.conf
```
* Install, configure, and run **postgresql**
* Execute
```bash
python worker.py
cherryd -i webApp -c dev.conf
```
##Run on Heroku
* Clone the repository
```bash
git clone https://github.com/Ale46/google-drive-to-rss.git
```
* Create your heroku project
```bash
heroku create
```
* Add postgresql addon
```bash
heroku addons:add heroku-postgresql
```
* Deploy on heroku

Side note: the worker and the web part will run in one dyno. It's a bad practice, but you will be not charged by Heroku. You can edit ```./bin/web``` to define two dynos, one for worker.py and one for the web part.
###Issues
Google drive files (docs, sheets, etc.) will be ignored and not included in the rss feed.
