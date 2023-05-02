# SummerPlaylist
Generate a list of candidate songs for my annual summer playlist

## Outcomes


## Process
### Spotify Setup
Sign in to [Spotify](https://developer.spotify.com/dashboard/applications) Account and accept Terms of Service
Register new Webapp to get credentials

### Local Setup
Create GitHub repository
Clone repository to local machine (I prefer to do this in VSCode using the Command Palette and the "GitHub Pull Requests and Issues" extension)
Create new conda environment
`$ conda create -n summerplaylist python=3.10.8`
`$ conda activate summerplaylist`
Install packages
`$ pip install -r requirements.txt`
Save Spotify credentials as environment variables
`$ conda env config vars set CLIENTID="<my_client_ID>"`  
`$ conda env config vars set CLIENTSECRET="<my_client_secret>"` 
`$ conda env config vars set REDIRECT_URI="https://localhost:5000/"` 
Check that environment variables were saved correctly 
`$ conda env config vars list`

### Choose a Wrapper
Why reinvent the wheel?
sandbox.ipynb
spotipy vs. tekore
[Spotipy Reference](https://spotipy.readthedocs.io/en/2.22.1/#api-reference)
[Tekore Reference](https://tekore.readthedocs.io/en/stable/reference/client.html)

### Collect list of candidate artists
collectArtists.ipynb
websites:
https://www.musicfestivalwizard.com/festivals/
personal favorites:
my spotify account
Export these to "artists1.csv"

### Collect list of candidate songs
artistsToSongs.ipynb
Read in list of candidate artists in "artists.csv"
Search Spotify for their Spotify IDs
Find any of their top songs from the last 5 years
Export these to "songs1.csv"

### Write these to a Spotify "Artist Candidates" playlist
songsToPlaylist1.ipynb
Read in list of songs in "songs1.csv"
Create an empty "Artist Candidates" Spotify playlist
Add the songs to the playlist

### Listen to the "Artist Candidates"
Select any artists you like and add one of their songs to a playlist for the current year

### Create playlist based on candidate songs
collectArtists2.ipynb
Get a list of all artists who appeared on my previous summer playlists or the current summer candidates
Find any of their albums from the last 3 years
Find the song IDs from these albums
Export these to songs2.csv

### Listen and delete uninteresting songs


### Round 2: Generate more candidate songs based on slimmed-down candidates