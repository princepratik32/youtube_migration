# youtube_migration
This is a simple script I wrote to migrate my Spotify playlists to YouTube music one at a time. Here's how to use it.

## Step 1: Obtain API Keys for Youtube and Spotify
For YouTube API, signup/login to Google Cloud console and then create an API key and OAuth2.0 client ID, as well as OAuth consent screen. Make sure you give at least YouTube Data API V3 scope to your API key/client

For Spotify, sign up/in for Spotify for Developers site and create an API key there.

For both of these, you would need 3 things:
- API Key
- API Secret
- Client ID

## Step 2: Authenticate your accounts
### For YouTube
- Go to `https://accounts.google.com/o/oauth2/v2/auth?scope=https%3A%2F%2Fwww.googleapis.com%2Fauth%2Fyoutube&access_type=offline&include_granted_scopes=true&state=state_parameter_passthrough_value&redirect_uri=http%3A%2F%2Flocalhost&response_type=code&client_id=<YOUR_ACTUAL_CLIENT_ID>`
- After approving the data access, it would redirect you to a localhost URL like `http://localhost/?state=state_parameter_passthrough_value&code=<SUPER_SECRET_CODE_THAT_GOOGLE_GAVE_YOU>&scope=https://www.googleapis.com/auth/youtube` Remember: You would need to add `http://localhost` to your API key's redirect URL from Google Cloud console.
- Use the `code` from previous step to make an HTTP call like: `curl --data "code=<SECRET_CODE_GOES_HERE>&client_id=<CLIENT_ID>&client_secret=<ULTRA_SECRET_API_SECRET>&redirect_uri=http://localhost&grant_type=authorization_code" https://oauth2.googleapis.com/token` That should give you `access_token` which you can use to make API calls for about an hour. It will also give you a `refresh_token`, keep it safe. You can use it to refresh your `access_token` when it expires.
- Refresh the `access_token` using: `curl --data "client_id=<YOUR CLIENT ID>&client_secret=<YOUR API SECRET>&grant_type=refresh_token&refresh_token=<REFRESH_TOKEN_FROM_THE_PREVIOUS_STEP>" https://oauth2.googleapis.com/token`


### For Spotify
- Go to `https://accounts.spotify.com/authorize?response_type=code&client_id=<YOUR SPOTIFY CLIENT ID>&scope=playlist-read-private&redirect_uri=http://localhost`
- After authenticating the app, you'd be redirected to localhost endpoint like: `http://localhost/?code=<VERY SECRET CODE>`
- Create a Basic auth token like: `echo -n 'client_id:client_secret' | base64` (discard any newline in this output. Your token is a string in a single line) and make a POST call like: `url -X POST --data 'code=<SECRET CODE FROM PREVIOUS STEP>&grant_type=authorization_code&redirect_uri=http://localhost' -H 'Authorization: Basic <TOKEN CREATED USING YOUR API KEY'S CLIENT_ID & CLIENT_SECRET>' -H 'Content-Type: application/x-www-form-urlencoded' https://accounts.spotify.com/api/token`
- This should give you access_token and refresh_token to use.
- You can refresh the token using: `curl -X POST --data "grant_type=refresh_token&refresh_token=<YOUR REFRESH TOKEN FROM PREVIOUS STEP>" -H "Authorization: Basic <YOUR BASIC TOKEN FROM PREVIOUS STEP>" -H "Content-Type: application/x-www-form-urlencoded" https://accounts.spotify.com/api/token`

## Step 3: Get yourself couple of playlist IDs, source (Spotify) & destination (YouTube music)
- For Spotify, you can fetch playlists using an API calls. But it's easier to simply open the Spotify web client and extract it from the URL like `https://open.spotify.com/playlist/3IIwBZPVmBrva1zszVRZ5I` where `3IIwBZPVmBrva1zszVRZ5I` is the playlist ID.
- Similarly, you need to first create a playlist on YouTube music and open it in the web player. **However**, when you open a playlist page `https://music.youtube.com/browse/VLPLcvO-lt9W-7Noyp5HNztvkanrgPQ3m7mM`, the playlist ID is `PLcvO-lt9W-7Noyp5HNztvkanrgPQ3m7mM` i.e. remove ignore `VP` in the playlist string. Don't know why, ask Google.


## Step 4: Run the script with Python 3.12
- `python3.12 playlist_migration.py <spotify_token> <youtube_token> <spotify_playlist> <youtube_playlist>`. It would ask you to select a YouTube search result for each song of the playlist. Just type the number and hit enter. If you want to select the first one, skip entering a number, just hit enter. 😎

**Important note:** Google restricts API key usage unless you pay them or get increased quota. It's 10,000 points per day, and WRITE action takes 50 points, so you can add up to 200 songs to your playlists like this per day.