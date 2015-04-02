# coding=UTF-8
# -*- coding: UTF-8 -*-
import os
import psycopg2
import cherrypy
from cherrypy.lib.static import serve_file
from feedgen.feed import FeedGenerator
import ConfigParser

current_dir=os.path.dirname(os.path.abspath(__file__))

config = ConfigParser.ConfigParser()
if os.path.isfile("local.conf"):
    config.read("local.conf")
    db = psycopg2.connect(host = config.get('Database', 'hostname'), database = config.get('Database', 'database'), user = config.get('Database', 'username'), password = config.get('Database', 'password'))
else:
    import urlparse
    urlparse.uses_netloc.append('postgres')
    url = urlparse.urlparse(os.environ['DATABASE_URL'])
    db = psycopg2.connect("dbname=%s user=%s password=%s host=%s " % (url.path[1:], url.username, url.password, url.hostname))
config.read(["options.conf", "rss.conf",])

cursor = db.cursor()

class Root:

    @cherrypy.expose
    def index(self):
        return "\
        <html>\
        <head>\
        <title>Google Drive to Rss</title>\
        </head>\
        <body>\
        Google Drive to Rss - <a href=\"http://github.com/Ale46/google-drive-to-rss\" />\
        </body>\
        </html>"

    @cherrypy.expose
    def rss(self, name):
        cherrypy.response.headers['Content-Type'] = 'application/rss+xml'
        fg = FeedGenerator()
        cursor.execute("SELECT * FROM RSS WHERE source = %s ORDER BY filedate DESC;", (name,))
        fg.id(config.get('Options', 'rss_url') + name)
        fg.title(config.get(name, 'rss_title'))
        fg.description(config.get(name, 'rss_desc'))
        fg.link( href=config.get('Options', 'rss_url')+name, rel='alternate' )
        for row in cursor:
            fe = fg.add_entry()
            fe.id('https://drive.google.com/uc?id='+row[1]+'&export=download')
            fe.title(config.get(name, 'feed_entry_prepend')+row[2]+config.get(name, 'feed_entry_postpend'))
            fe.description(row[2] + ' - https://drive.google.com/uc?id='+row[1]+'&export=download')
        return fg.rss_str(pretty=True)

cherrypy.config.update({'server.socket_host': '0.0.0.0',})
cherrypy.config.update({'server.socket_port': int(os.environ.get('PORT', config.get('Options', 'server_port'))),})
