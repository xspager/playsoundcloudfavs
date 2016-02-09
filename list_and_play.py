import os, sys
import subprocess
import sqlite3

import soundcloud

def write_raw(raw_str):
	#sys.stdout.buffer.write(raw_str)
	sys.stdout.write(raw_str)
	#sys.stdout.buffer.flush()
	sys.stdout.flush()


def pick_a_fav_track(client): 

	favorite_tracks = client.get('/me/favorites', limit=100)
	
	for num, track in enumerate(favorite_tracks):
		#import pdb; pdb.set_trace()
		write_raw(("%d) %s\n" % (num, track.title)).encode("utf8"))
	
	num = int(input("\nTrack: "))
	track = favorite_tracks[num]
	
	return track


def pick_track_from_following(client): 

	followings = client.get('/me/followings', limit=100).collection
	
	for num, following in enumerate(followings):
		#import pdb;pdb.set_trace()
		write_raw(("%d) %s\n" % (num, following.username)).encode("utf8"))
	
	num = int(input("\nFollowing: "))
	following = followings[num]
	
	playlists = client.get("/users/%i/playlists" % following.id, limit=100)

	for num, playlist in enumerate(playlists):
		write_raw(("%d) %s\n" % (num, playlist.title)).encode("utf8"))

	num = int(input("\nPlaylist: "))
	playlist = playlists[num]

	for num, track in enumerate(playlist.tracks):
		write_raw(("%d) %s\n" % (num, track['title'])).encode("utf8"))

	track = client.get(track['uri'])
	import pdb;pdb.set_trace()

	return track


def pick_playlist_from_following(client): 

	followings = client.get('/me/followings', limit=100).collection
	
	for num, following in enumerate(followings):
		#import pdb;pdb.set_trace()
		write_raw(("%d) %s\n" % (num, following.username)).encode("utf8"))
	
	num = int(input("\nFollowing: "))
	following = followings[num]
	
	playlists = client.get("/users/%i/playlists" % following.id, limit=100)

	for num, playlist in enumerate(playlists):
		write_raw(("%d) %s\n" % (num, playlist.title)).encode("utf8"))

	num = int(input("\nPlaylist: "))
	playlist = playlists[num]

	return playlist


def play_playlist(client, playlist):

	for num, track in enumerate(playlist.tracks):
		track = client.get(track['uri'])

		play_track(client, track)


def play_track(client, track):
	# get the tracks streaming URL
	stream_url = track.stream_url
	
	# get music file
	resp = soundcloud.request.make_request('get', track.stream_url, dict(
		oauth_token=client.access_token,
		client_id=client.client_id)
	)

	# print the tracks stream URL
	write_raw(("\nPlaying: %s\n" % track.title).encode('utf8'))
	write_raw(("By: %s\n" % track.user['username']).encode('utf8'))
	
	mpg123 = subprocess.Popen(['mpg123', '-q', '-'], stdin=subprocess.PIPE)
	
	mpg123.communicate(resp.content)
	
	#subprocess.call(['mpg123', '-q', stream_url])


if __name__ == "__main__":

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
	
	print("\nHello, %s!\n" % me.username)
	
	#track = pick_a_fav_track(client)

	#track = pick_track_from_following(client)
	#play_track(client, track)

	playlist = pick_playlist_from_following(client)
	play_playlist(client, playlist)
