# SummerPlaylist
Generate a list of candidate songs for my annual summer playlist

## Outcomes


## Process
### Spotify Setup
Sign in to [Spotify](https://developer.spotify.com/dashboard/applications) Account and accept Terms of Service
Register new Webapp to get credentials

### Local Setup
Create GitHub repository
Clone repository to local machine (I do this using the VSCode Command Palette)
Create new conda environment
`$ conda create -n summerplaylist python=3.10.8`
`$ conda activate summerplaylist`
Install packages
`$ pip install -r requirements.txt`
Save Spotify credentials as environment variables
`$ conda env config vars set CLIENTID="<my_client_ID>"`  
`$ conda env config vars set CLIENTSECRET="<my_client_secret>"` 
Check that environment variables were saved correctly 
`$ conda env config vars list`

### Choose a Wrapper
Why reinvent the wheel?
spotipy vs. tekore
[Spotipy Reference](https://spotipy.readthedocs.io/en/2.22.1/#api-reference)
[Tekore Reference](https://tekore.readthedocs.io/en/stable/reference/client.html)
sandbox.ipynb

### Collect list of candidate artists
websites:
https://www.musicfestivalwizard.com/festivals/
personal favorites:
my spotify account

### Collect list of candidate songs


### Create playlist based on candidate songs


### Listen and delete uninteresting songs


### Round 2: Generate more candidate songs based on slimmed-down candidates