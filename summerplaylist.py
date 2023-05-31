# Config
import time
from datetime import datetime
from dateutil.relativedelta import relativedelta
from collections import Counter
import pandas as pd
import numpy as np
from requests_html import HTMLSession
import tekore as tk


## Authenticate to Spotify
def authenticateToSpotify(CLIENTID, CLIENTSECRET, REDIRECT_URI):
    # Get client token
    app_token = tk.request_client_token(CLIENTID, CLIENTSECRET)
    # Get a user token; Note the need to ask for write scope in order to create/edit playlists
    # This will open a browser window; the user will need to copy the URL from the browser and paste it into the VSCode Command Palette
    user_token = tk.prompt_for_user_token(CLIENTID, CLIENTSECRET, REDIRECT_URI, scope=[tk.scope.write, tk.scope.playlist_read_private])
    # Create spotify instance
    spotify = tk.Spotify(app_token)
    # Get the user's spotifyID; The spotify instance will have to reference the user_token to be authorized for this data
    with spotify.token_as(user_token):
        userID = spotify.current_user().id
    return spotify, userID, user_token


## GET from third party sources

# Function to scrape list of artist names from MusicFestivalWizard
def fetchMusicFestivalWizard():
    session = HTMLSession()
    r = session.get('https://www.musicfestivalwizard.com/all-festivals/')
    artists = r.html.find('#artist', first=True).find('option')
    artistList = [x.text for x in artists]
    result = pd.DataFrame({'artistName':artistList})
    result = result.loc[result.artistName!="All Artists"]
    return result


## GET from Spotify

# Get artist info based on artist name
def fetchArtistInfo(credentials, artists):
    spotify, userID, user_token = credentials
    try:
        # Search spotify for artists based on name
        possibleArtists, = spotify.search(artists['artistName'], types=['artist'], limit=1)
        # Select the first search result
        artists['artistID'] = possibleArtists.items[0].id
        artists['artistPopularity'] = possibleArtists.items[0].popularity
        artists['artistFollowers'] = possibleArtists.items[0].followers.total
        artists['artistGenre'] = ", ".join(list(possibleArtists.items[0].genres))
        result = artists
    except:
        artists['artistID'] = np.nan
        artists['artistPopularity'] = np.nan
        artists['artistFollowers'] = np.nan
        artists['artistGenre'] = np.nan
        result = artists
    finally:
        # Wait 2 seconds so we do not exceed our API call allowance
        time.sleep(2)
        return result

# GET the top tracks for each artist based on a list of artistIDs
def fetchTopSongs(credentials, artistIDs, maxAge=5):
    spotify, userID, user_token = credentials
    # Only select top songs from the last few years (default 5 years)
    dateMin = datetime((datetime.today() - relativedelta(years=maxAge)).year, 3, 17)
    # Create empty list
    songURIs = []
    for artistID in artistIDs:
        try:
            # Query the spotify API
            topSongs = spotify.artist_top_tracks(artistID, "US")
            # Iterate over the tracks to find a list of songURIs;
            # Limit this to only those songs produced in the last few years; Use only the year (first four digits)
            # Limit this to only three songs per artist
            result = [x.uri for x in topSongs if datetime.strptime(x.album.release_date[:4], '%Y')>dateMin][:3]
        except: 
            result = []
        finally:
            # Append songs to list
            songURIs += result
            # Wait 2 seconds so we do not exceed API limits
            time.sleep(2)
    return songURIs

# GET albums released in recent years based on artistIDs
def fetchRecentAlbums(credentials, artistIDs, maxAge):
    spotify, userID, user_token = credentials
    # Only take albums released in the last few years
    dateMin = datetime((datetime.today() - relativedelta(years=maxAge)).year, 3, 17)
    dateMax = datetime((datetime.today()).year, 3, 17)
    # Album words to exclude
    excludeList = 'Deluxe|Extended|Remix'
    # Create empty list
    albums = []
    # Loop through list of artists
    for artistID in artistIDs:
        try:
            # Query the spotify API for that artist's albums
            query = spotify.artist_albums(artistID, limit=50, include_groups=['album']).items
            result = pd.DataFrame([{'albumID':x.id, 'albumName':x.name, 'albumReleaseDate':x.release_date} for x in query])
            # Filter out albums older than three years
            result['albumReleaseDate'] = pd.to_datetime(result['albumReleaseDate'])
            result = result.loc[(result["albumReleaseDate"]>=dateMin) & (result["albumReleaseDate"]<=dateMax)]
            # Filter out re-issues of older albums
            result = result.loc[~result['albumName'].str.contains(excludeList, regex=True)]
            # Get only the list of albumIDs
            additions = list(result['albumID'])
        except: 
            # If exception, fill in blank data
            additions = []
        finally:
            # Wait 2 seconds so we do not exceed our API call allowance
            time.sleep(2)
            # Append the recent albums to the list
            albums += additions
    # Remove duplicates
    albums = list(set(albums))
    return albums

# GET all tracks from an album based on albumID
def fetchTracks(credentials, albumIDs):
    spotify, userID, user_token = credentials
    with spotify.token_as(user_token):
        # Cut the df into chunks
        n = 0
        trackURIs = []
        while n < len(albumIDs):
            albumsToGet = albumIDs[n:(n+20)]
            try:
                    # Query spotify for that album's tracks
                    nestedList = [[y.uri for y in x.tracks.items] for x in spotify.albums(albumsToGet, market='from_token')]
                    # Unnest the list 
                    tracks = [item for sublist in nestedList for item in sublist]
                    trackURIs += tracks
                    # Wait 2 seconds so we do not exceed our API call allowance
                    time.sleep(2)
            except:
                    # If there is an error in the batch, go through each separately
                    for albumID in albumsToGet:
                        try:
                            nestedList = [[y.uri for y in x.tracks.items] for x in spotify.album(albumID, market='from_token')]
                            # Unnest the list 
                            tracks = [item for sublist in nestedList for item in sublist]
                            trackURIs += tracks
                            # Wait 2 seconds so we do not exceed our API call allowance
                            time.sleep(2)
                        except: 
                            pass
            finally:
                n += 20
    # Drop duplicates
    trackCounter = Counter(trackURIs)
    result = [x[0] for x in trackCounter.items()]
    return result

# GET artistIDs based on playlistID
def fetchArtistsFromPlaylist(credentials, playlistID):
    spotify, userID, user_token = credentials
    offset = 0
    limit = 100
    nestedList = ["empty"]
    result = []
    # Loop through the offsets until there are no more trac ks
    while len(nestedList) > 0:    # Get all artists in the list from spotify
        nestedList = [[y.id for y in x.track.artists] for x in spotify.playlist_items(playlistID, offset=offset, limit=limit).items]
        # Unnest the list 
        unnestedList = [item for sublist in nestedList for item in sublist]
        # Concatenate new additions
        result += unnestedList
        # Increment counter
        offset += 100
    return result

# Get tracks and track info based on playlistID
def fetchTracksFromPlaylist(credentials, playlistID):
    spotify, userID, user_token = credentials
    offset = 0
    limit = 100
    nestedList = ["empty"]
    result = pd.DataFrame()
    # Loop through the offsets until there are no more trac ks
    while len(nestedList) > 0:
        # Get all artists in the list from spotify
        nestedList = [[{
            "artistName":y.name, "artistID":y.id, "trackName":x.track.name, "release_date":x.track.album.release_date, "songURI":x.track.uri
            } for y in x.track.artists
            ] for x in spotify.playlist_items(playlistID, offset=offset, limit=limit).items]
        # Unnest the list 
        unnestedList = [item for sublist in nestedList for item in sublist]
        toAdd = pd.DataFrame(unnestedList)
        # Concatenate new additions
        result = pd.concat([result, toAdd], axis=0, ignore_index=True)
        # Increment counter
        offset += 100
    return result

## POST to Spotify

# Create playlist based on string
def getPlaylistID(credentials, playlistName):
    spotify, userID, user_token = credentials
    with spotify.token_as(user_token):
        # Check if playlist already exists; if not create a new one
        userPlaylists = pd.DataFrame([{'id':x.id, 'name':x.name} for x in spotify.playlists(userID, limit=40).items])
        if not (userPlaylists['name'].eq(playlistName)).any():
            # Create a playlist for the user
            newPlaylist = spotify.playlist_create(userID, playlistName, public=False, description='Recent albums from new artists')
            playlistID = newPlaylist.id
        # Else just get playlistID
        else:
            playlistID = userPlaylists.loc[userPlaylists['name']==playlistName, 'id'].reset_index(drop=True)[0]
    return playlistID

# Add songs to playlist based on songURI
def addToPlaylist(credentials, URIList, playlistID):
    spotify, userID, user_token = credentials
    with spotify.token_as(user_token):
        # Counter
        n = 0
        # Add songs in chunks of 100
        while n < len(URIList):
            toAdd = URIList[n:(n+100)]
            spotify.playlist_add(playlistID, toAdd, position=None)
            # Wait two seconds to avoid exceeding API limits
            time.sleep(2)
            # Increment counter
            n += 100