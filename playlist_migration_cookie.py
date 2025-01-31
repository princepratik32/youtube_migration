import json
import requests
import sys
import os


# Make sure there are 5 input arguments
if len(sys.argv) != 6:
	print("Usage: python3 plyalist_migration_cookie.py <source_playlist> <destination_playlist> <spotify_token> <youtube_cookie> <youtube_auth>")
	sys.exit(1)

spotifyPlaylist = sys.argv[1]
youtubePlaylist = sys.argv[2]
spotifyToken = sys.argv[3]
youTubeCookie = sys.argv[4]
youTubeAuth = sys.argv[5]

baseSpotifyEndpoint = "https://api.spotify.com/v1"

# fetch Spotify playlist items
def getSpotifyPlaylistItems(playlistId):
	playlistItems = []
	playlistUrl = baseSpotifyEndpoint + "/playlists/" + spotifyPlaylist + "/tracks"
	payload = {'limit': 50}

	while True:
		response = requests.get(playlistUrl, headers={'Authorization': 'Bearer ' + spotifyToken}, params=payload)
		if response.status_code == 200:
			playlistData = response.json()
			playlistItems += playlistData['items']
			if playlistData['next'] is None:
				break
			playlistUrl = playlistData['next']
		else:
			print("Error fetching Spotify playlist items" + response.text + " " + str(response.status_code))
			sys.exit(1)

	return playlistItems

def searchOnYoutube(searchQuery):
	'''
	This is a method to search for a song on YouTube using the YouTube search API WITHOUT using your own API key/OAuth token.
	This is straight up copied request from the browser when you search for a song on YouTube.
	'''
	searchUrl = "https://www.youtube.com/youtubei/v1/search"
	payload = {
		"context": {
			"client": {
				"clientName": "WEB",
				"clientVersion": "2.20250127.01.00"
			}
		},
		"query": searchQuery
	}

	response = requests.post(searchUrl, data=json.dumps(payload), headers={'Content-Type': 'application/json'})
	if response.status_code != 200:
		print("Error fetching YouTube search results" + response.text + " " + str(response.status_code))
		sys.exit(1)
	responseData = response.json()
	return responseData

def parseYoutubeSearchResponse(responseData):
	'''
	The API response is quite verbose, so parse it cleanly.
	'''
	searchResultList = []
	for item in responseData['contents']['twoColumnSearchResultsRenderer']['primaryContents']['sectionListRenderer']['contents'][0]['itemSectionRenderer']['contents']:
		if 'videoRenderer' in item:
			videoRenderer = item['videoRenderer']
			searchResultList.append({'videoId': videoRenderer['videoId'], 'title': videoRenderer['title']['runs'][0]['text'], 'channelTitle': videoRenderer['ownerText']['runs'][0]['text']})

	return searchResultList


def clear():
	'''
	Clear the console screen
	'''
	if os.name == 'nt':
		os.system('cls')
	else:
		os.system('clear')

spotifyResponse = getSpotifyPlaylistItems(spotifyPlaylist)
songList = []

# Extract song details from Spotify response
for song in spotifyResponse:
	track = song['track']
	songList.append(track['name'] + " by " + track['artists'][0]['name'])

totalsongs = len(songList)
for playlistIndex, song in enumerate(songList):
	clear()
	# Print progress
	print("Adding : " + str(playlistIndex + 1) + " of " + str(totalsongs) + " : " + song)

	# Search for the song on YouTube and extract videoId, vidoe title and channel title from YouTube response
	searchResultList = parseYoutubeSearchResponse(searchOnYoutube(song + " official"))

	# Ask the user to select a video
	for index, video in enumerate(searchResultList):
		print(str(index) + ". CHANNEL => " + video['channelTitle'] + " TITLE => " + video['title'])
	selectedIndex = int(input("Select a video: ") or 0)

	if selectedIndex < 0 or selectedIndex >= len(searchResultList):
		print("Invalid selection")
		sys.exit(1)

	# Add the selected video to the destination playlist
	videoId = searchResultList[selectedIndex]['videoId']

	youtubeEditPlaylistURL = 'https://music.youtube.com/youtubei/v1/browse/edit_playlist'
	body = {
		'context': {
			'client': {
				'clientName': 'WEB_REMIX',
				'clientVersion': '1.20250127.01.00'
			}
		},
		'actions': [
			{
				'addedVideoId': videoId,
				'action': 'ACTION_ADD_VIDEO'
			}
		],
		'playlistId': youtubePlaylist
	}

	response = requests.post(youtubeEditPlaylistURL, headers={'Authorization': youTubeAuth, 'Content-Type': 'application/json', 'Cookie': youTubeCookie, 'Origin': 'https://music.youtube.com'}, data=json.dumps(body))

	if response.status_code != 200:
		print("Error adding song " + searchResultList[selectedIndex]['title'] + " to YouTube playlist" + response.text + " " + str(response.status_code))
		sys.exit(1)	
	
	print("Added " + searchResultList[selectedIndex]['title'] + " to YouTube playlist")