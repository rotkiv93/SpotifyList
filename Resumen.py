import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import pymsteams
import os
from datetime import datetime
from PollAnalyzer import getAllPollAnalytics
from Utils import parseTrackName, getTopResults
from dotenv import load_dotenv

# GET .env VARIABLES
load_dotenv()
SPOTIFY_CLIENT_ID = os.environ('SPOTIFY_CLIENT_ID')
SPOTIFY_CLIENT_SECRET = os.environ('SPOTIFY_CLIENT_SECRET')
TEAMS_WEBHOOK_URL = os.environ('TEAMS_WEBHOOK_URL')
TEAMS_WEBHOOK_URL_TEST = os.environ('TEAMS_WEBHOOK_URL_TEST')

client_credentials_manager = SpotifyClientCredentials(
    client_id=SPOTIFY_CLIENT_ID, client_secret=SPOTIFY_CLIENT_SECRET)
sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)

# Get playlist actual info
playlist = sp.playlist('4xnIIGuxf2f5UoLR7mXY4u')


class Row():
    def __init__(self):
        self.addedbById = None
        self.addedbByHref = None
        self.addedByImg = None
        self.addedDate = None
        self.trackName = None
        self.trackHref = None
        self.trackImg = None
        self.artistName = None


Tracks = []
Users = []
for track in playlist['tracks']['items']:

    newRow = Row()
    # Get User info
    userId = track['added_by']['id']
    user = sp.user(userId)
    Users.append(user['display_name'])
    newRow.addedbById = user['display_name']
    newRow.addedbByHref = user['external_urls']['spotify']

    if (len(user['images']) > 0):
        newRow.addedByImg = user['images'][0]['url']
    else:
        newRow.addedByImg = "https://pbs.twimg.com/media/BYUoauICYAA_jHx.jpg"

    newRow.addedDate = datetime.strptime(
        track['added_at'], '%Y-%m-%dT%H:%M:%SZ')

    # Get Track info
    newRow.trackName = track['track']['name']
    newRow.trackHref = track['track']['external_urls']['spotify']
    newRow.trackImg = track['track']['album']['images'][0]['url']

    # Get artists
    artists = track['track']['artists']
    artistName = ''
    for index, artist in enumerate(artists):
        if (len(artists) == 1):
            artistName = artist['name']
        else:
            if (index == len(artists) - 1):
                artistName += artist['name']
            else:
                artistName = artistName + artist['name'] + ', '

    newRow.artistName = artistName
    Tracks.append(newRow)

Tracks.sort(key=lambda x: x.addedbById)

## ---------------- Doing calculations for the data ---------------- ##
# Wall of shame calculations
wallOfShame = {}
filteredUserList = list(dict.fromkeys(Users))

# Count number of times a user appears in the Tracks List
for user in filteredUserList:
    userCount = 0
    for track in Tracks:
        if (track.addedbById == user):
            userCount += 1

    if (userCount != 2):
        wallOfShame[user] = userCount

## ---------------- Creating the table message ---------------- ##
teamsMsg = ""
# Adding the table header
teamsMsg += "<table><thead><tr><th>Canción</th><th>Añadida por</th><th>Hace</th></tr></thead><tbody>"

# Adding the table body
teamsMsgBody = ""
for track in Tracks:
    calcAddedDate = datetime.now() - track.addedDate
    teamsMsgBody += "<tr><td><a href='" + track.trackHref + "'>" + track.trackName + " - " + track.artistName + "</a></td>" + \
        "<td><a href='" + track.addedbByHref + \
        "'>" + track.addedbById + "</a></td><td>" + \
        str(calcAddedDate).split(",", 1)[0] + "</td></tr>"

teamsMsg += teamsMsgBody

# Closing the table tag
teamsMsg += "</tbody></table>"

## ---------------- Sending the message to teams ---------------- ##
myTeamsMessage = pymsteams.connectorcard(TEAMS_WEBHOOK_URL_TEST)

# Add color to the message
myTeamsMessage.color('#db03fc')

myTeamsMessage.text(
    '<div><h1 style="text-align:center;font-size:30px;color:#db03fc;" ><b> &#128140 Resumen de la playlist de la semana: ' + str(datetime.now().day) + "/" + str(datetime.now().month) + '/' + str(datetime.now().year) + '&#128140 </b></h1></div>')

# Setting First Section
Section1 = pymsteams.cardsection()
Section1.text(teamsMsg)
myTeamsMessage.addSection(Section1)

# Setting Second Section
Section2 = pymsteams.cardsection()
section2Title = '<div><h1 style="text-align:center;font-size:45px;color:#4287f5;" ><b> &#128128 Wall of Shame &#128128 </b></h1></div>'
section2Body = '<div style="text-align:center;" ><img style="width:300px;" width="300" height="300" src="https://i1.sndcdn.com/artworks-000354524928-586iiw-t500x500.jpg"></img></div>'

for key, value in wallOfShame.items():
    if (key != 'Victor Lamas'):
        if value == 0:
            section2Body += '<br/><h2 style="text-align:center;">' + \
                str(key) + ': No has añadido ninguna canción</h2>'
        if value == 1:
            section2Body += '<br/><h2 style="text-align:center;">' + \
                str(key) + ': Solo has añadido ' + \
                str(value) + ' canción' + '</h2>'
        if (value > 1):
            section2Body += '<br/><h2 style="text-align:center;">' + \
                str(key) + ': Te has pasado y has añadido' + \
                str(value) + ' canciones' + '</h2>'

Section2.text(section2Title + "<br/>" + section2Body)
myTeamsMessage.addSection(Section2)

## SECTION 3 - WINNER AND LOSER ##
analytics = getAllPollAnalytics()

Section3 = pymsteams.cardsection()

# Setting the title of the section.
section3Title = '<h1 style="text-align:center;font-size:45px;color:#4287f5;" > <b> &#128064 Resultados de la votación: &#128064 </b> </h1>'
section3TextWinner = '<h2 style="text-align:center;font-size:30px;color:#fcba03;" > &#11088 &#11088 El ganador de la semana &#11088 &#11088 </h2> <br/>'
section3TextLoser = '<h2 style="text-align:center;font-size:30px;color:#fc4103;">&#10060 &#10060 El perdedor de la semana &#10060 &#10060</h2> <br/>'

# Getting winners and losers track name
winnersTrackName = []
losersTrackName = []

resWinners = getTopResults(analytics['pollWinner']['Tracks'])
resLosers = getTopResults(analytics['pollLoser']['Tracks'])

for track in resWinners:
    winnersTrackName.append(parseTrackName(track))

for track in resLosers:
    losersTrackName.append(parseTrackName(track))

# Setting the winner section
for track in Tracks:
    if (track.trackName in winnersTrackName):
        section3TextWinner += '<div style="text-align:center;" align="center"> <img style="width:200px;" src="' + \
            track.addedByImg + '"> </img><img style="width:200px;" src="' + \
            track.trackImg + '"></img></div>'
        section3TextWinner += '<div style="font-size:45px;color:#fcba03;" align="center"> <h1> <b>' + \
            track.addedbById + ' - ' + track.trackName + \
            ' - ' + track.artistName + '</b></h1> <h2 style="color:#fcba03" > Con ' + \
            str(analytics['pollWinner']['Tracks']
                [0].votes) + ' votos </h2> <br/> </div>'

# Setting the loser section
for track in Tracks:
    if (track.trackName in losersTrackName):
        section3TextLoser += '<div style="text-align:center;" align="center"> <img style="width:200px;" src="' + \
            track.addedByImg + '"> </img><img style="width:200px;" src="' + \
            track.trackImg + '"></img></div>'
        section3TextLoser += '<div style="font-size:45px;color:#fc4103;" align="center"> <h1> <b>' + \
            track.addedbById + ' - ' + track.trackName + \
            ' - ' + track.artistName + '</b></h1> <h2 style="color:#fc4103" > Con ' + \
            str(analytics['pollLoser']['Tracks']
                [0].votes) + ' votos </b> </h2> <br/> </div>'

Section3.text("<div> " + section3Title + section3TextWinner +
              "<br/>" + section3TextLoser + "</div>")
myTeamsMessage.addSection(Section3)


# # Send the message.
myTeamsMessage.send()
