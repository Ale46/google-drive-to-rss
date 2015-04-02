from lxml import html
import requests
import psycopg2
from datetime import datetime
import ConfigParser
import time
import schedule
import os.path


def get_config(section):
    dict1 = {}
    options = config.options(section)
    for option in options:
        try:
            dict1[option] = config.get(section, option)
            if dict1[option] == -1:
                print("skip: %s" % option)
        except:
            print("exception on %s!" % option)
            dict1[option] = None
    return dict1


config = ConfigParser.ConfigParser()
if os.path.isfile("local.conf"):
    print("Starting locally")
    config.read("local.conf")
    db = psycopg2.connect(host = config.get('Database', 'hostname'), database = config.get('Database', 'database'), user = config.get('Database', 'username'), password = config.get('Database', 'password'))
else:
    import urlparse
    urlparse.uses_netloc.append('postgres')
    url = urlparse.urlparse(os.environ['DATABASE_URL'])
    db = psycopg2.connect("dbname=%s user=%s password=%s host=%s " % (url.path[1:], url.username, url.password, url.hostname))

config.read("rss.conf")
config.remove_section("Database")
rss_list = config.sections()

cursor = db.cursor()
cursor.execute("CREATE TABLE IF NOT EXISTS RSS(id serial PRIMARY KEY, fileid VARCHAR(50) UNIQUE NOT NULL, filename VARCHAR(300) NOT NULL, filedate VARCHAR(26), source VARCHAR(100));")
db.commit()

def update(rss):
    address = (get_config((rss))['drive_link'])
    r = requests.get(address)
    pageReady = r.text
    print ("Updating ->" + rss + " ("+address+")")

    data = html.document_fromstring(pageReady)
    obj_ids = data.xpath('//div[@class="flip-entry"]')
    obj_names = data.xpath('//div[@class="flip-entry-title"]/text()')

    if (len(obj_ids)) != (len(obj_names)):
        print("Erorr, ids - names mismatch")
    else:
        max_item = int(get_config((rss))['max_item'])
        parsed_items_count = len(obj_ids)

        if parsed_items_count < max_item:
            itera =  range(0, parsed_items_count)
        else:
            itera = range(parsed_items_count - max_item, parsed_items_count)

        for i in itera:
            # [6:] remove "entry-" from id value
            obj_id = obj_ids[i].get('id')[6:]
            # cursor.execute("INSERT INTO RSS (fileid, filename, filedate, source)  SELECT (%s, %s, %s, %s) WHERE NOT EXISTS (SELECT * FROM RSS WHERE fileid=%s);", (obj_ids[i].get('id')[6:], obj_names[i], str(datetime.now()), rss,))
            cursor.execute("SELECT id FROM RSS WHERE fileid = %s;", (obj_id,))
            if not cursor.fetchone():
                cursor.execute("SELECT count(*) FROM RSS WHERE source = %s;", (rss,))
                if int(get_config((rss))['max_item']) == int(cursor.fetchone()[0]):
                    print("Limit reached, deleting oldest item from " + rss)
                    cursor.execute("DELETE FROM rss WHERE ctid in (SELECT ctid FROM rss WHERE source = %s ORDER BY filedate LIMIT 1);", (rss,))
                    #db.commit()
                print(obj_id + " - " + obj_names[i] + " - " + str(datetime.now()) + " - " + rss)
                cursor.execute("INSERT INTO RSS (fileid, filename, filedate, source) VALUES (%s, %s, %s, %s);", (obj_id, obj_names[i], str(datetime.now()), rss,))
        db.commit()

for rss in rss_list:
    schedule.every(float(get_config((rss))['check'])).minutes.do(update, rss)

schedule.run_all(10)

while 1:
    schedule.run_pending()
    time.sleep(1)
