import sys
import requests

# Make sure there are 4 input arguments
if len(sys.argv) != 5:
	print("Usage: python3 plyalist_migration.py <spotify token> <youtube token> <source_playlist> <destination_playlist>")
	sys.exit(1)

spotifyPlaylist = sys.argv[3]
youtubePlaylist = sys.argv[4]
spotifyToken = sys.argv[1]
youtubeToken = sys.argv[2]

baseSpotifyEndpoint = "https://api.spotify.com/v1"
baseYoutubeEndpoint = "https://www.googleapis.com/youtube/v3"

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


spotifyResponse = getSpotifyPlaylistItems(spotifyPlaylist)
songList = []

# Extract song details from Spotify response
for song in spotifyResponse:
	track = song['track']
	songList.append(track['name'] + " by " + track['artists'][0]['name'])

totalsongs = len(songList)
for index, song in enumerate(songList):
	# Print progress
	print("Adding : " + str(index + 1) + " of " + str(totalsongs) + " : " + song)

	# Search for the song on YouTube
	searchUrl = baseYoutubeEndpoint + "/search"
	payload = {'part': 'snippet', 'q': song + ' official', 'type': 'video', 'maxResults': 10}
	response = requests.get(searchUrl, params=payload, headers={'Authorization': 'Bearer ' + youtubeToken})
	if response.status_code != 200:
		print("Error fetching YouTube search results" + response.text + " " + str(response.status_code))
		sys.exit(1)
	responseData = response.json()

	# Extract videoId, vidoe title and channel title from YouTube response
	searchResultList = []
	for item in responseData['items']:
		searchResultList.append({'videoId': item['id']['videoId'], 'title': item['snippet']['title'], 'channelTitle': item['snippet']['channelTitle']})

	# Ask the user to select a video
	print("Select a video:")
	for index, video in enumerate(searchResultList):
		print(str(index) + ". CHANNEL => " + video['channelTitle'] + " TITLE => " + video['title'])
	selectedIndex = int(input())

	if selectedIndex < 0 or selectedIndex >= len(searchResultList):
		print("Invalid selection")
		sys.exit(1)

	# Add the selected video to the destination playlist
	videoId = searchResultList[selectedIndex]['videoId']

	playlistUrl = baseYoutubeEndpoint + "/playlistItems"
	payload = {'part': 'snippet'}
	body = '{"kind": "youtube#playlistItem", "snippet": {"resourceId":{"videoId": "' + videoId + '", "kind": "youtube#video"}, "playlistId":"' + youtubePlaylist + '"}}'

	response = requests.post(playlistUrl, params=payload, headers={'Authorization': 'Bearer ' + youtubeToken, 'Content-Type': 'application/json'}, data=body)

	if response.status_code != 200:
		print("Error adding song " + searchResultList[selectedIndex]['title'] + " to YouTube playlist" + response.text + " " + str(response.status_code))
		sys.exit(1)	
	
	print("Added " + searchResultList[selectedIndex]['title'] + " to YouTube playlist")