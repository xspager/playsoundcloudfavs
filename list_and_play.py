import os, sys
import sqlite3
import subprocess

import soundcloud

def write_raw(raw_str):
	sys.stdout.buffer.write(raw_str)
	sys.stdout.buffer.flush()

conn = sqlite3.connect('db.sqlite3')

c = conn.cursor()

c.execute("CREATE TABLE IF NOT EXISTS access_token(token TEXT)")

result = c.execute("SELECT token FROM access_token").fetchone()

if not result:
	# create client object with app credentials
	client = soundcloud.Client(client_id='77da88cf3b116f2828eaf0eeb39efb0c',
	                           client_secret='dbcd48991e9f4944798f79b35dde5136',
	                           redirect_uri='my-app://soundcloud/callback')
	
	# redirect user to authorize URL
	print("Go to the URL: %s" % client.authorize_url())
	code = input("Paste the code: ")
	token_obj = client.exchange_token(code)
	token = token_obj.access_token
	c.execute("INSERT INTO access_token VALUES (?)", (token,))
	conn.commit()
else:
	token = result[0]

client = soundcloud.Client(access_token=token)

me = client.get('/me')

print("Hello %s" % me.username)

favorite_tracks = client.get('/me/favorites')

for num, track in enumerate(favorite_tracks):
	#import pdb; pdb.set_trace()
	write_raw(("%d %s\n" % (num, track.title)).encode("utf8"))

num = int(input("Track: "))

for track in favorite_tracks[num:]:
	# get the tracks streaming URL
	stream_url = client.get(track.stream_url, allow_redirects=False)

	url = stream_url.location.replace('https', 'http')
	
	# print the tracks stream URL
	write_raw(("Playing: %s\n" % track.title).encode('utf8'))
	subprocess.call(['mpg123', '-q', url])
