import os
import requests
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from datetime import datetime
import pymsteams
import pickle
from dotenv import load_dotenv

# GET .env VARIABLES
load_dotenv()
ENDPOINT = "https://api.strawpoll.com/v3"
POLL_API_KEY = os.environ.get('POLL_API_KEY')

## GET THE SPOTIFY LIST INFORMATION ##
SPOTIFY_CLIENT_ID = os.environ.get('SPOTIFY_CLIENT_ID')
SPOTIFY_CLIENT_SECRET = os.environ.get('SPOTIFY_CLIENT_SECRET')

client_credentials_manager = SpotifyClientCredentials(
    client_id=SPOTIFY_CLIENT_ID, client_secret=SPOTIFY_CLIENT_SECRET)
sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)

# Get playlist actual info
playlist = sp.playlist('4xnIIGuxf2f5UoLR7mXY4u')

poll_options = []
for track in playlist['tracks']['items']:
    # Get Track info
    trackName = track['track']['name']

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

    poll_options.append({
        "type": "text",
        "value": trackName + " - " + artistName
    })

## SET THE POLL INFORMATION ##
payloadWinner = {
    "title": "Votación a MEJOR canción de la semana: " + str(datetime.now().day) + '/' + str(datetime.now().month) + '/' + str(datetime.now().year),
    "media": None,
    "poll_options": poll_options,
    "poll_config": {
        "is_private": False,
        "vote_type": "default",
        "allow_comments": False,
        "allow_indeterminate": False,
        "allow_other_option": False,
        "custom_design_colors": None,
        "deadline_at": None,
        "duplication_checking": "ip",
        "allow_vpn_users": False,
        "edit_vote_permissions": "nobody",
        "force_appearance": None,
        "hide_participants": True,
        "is_multiple_choice": True,
        "multiple_choice_min": 1,
        "multiple_choice_max": 5,
        "number_of_winners": 1,
        "randomize_options": False,
        "require_voter_names": False,
        "results_visibility": "always",
        "use_custom_design": False
    },
    "poll_meta": {
        "description": "Votación a mejor canción lista de Spotify: " + playlist['name'],
        "location": None,
    },
    "type": "multiple_choice",
}

## SET THE POLL INFORMATION ##
payloadLoser = {
    "title": "Votación a PEOR canción de la semana: " + str(datetime.now().day) + '/' + str(datetime.now().month) + '/' + str(datetime.now().year),
    "media": None,
    "poll_options": poll_options,
    "poll_config": {
        "is_private": False,
        "vote_type": "default",
        "allow_comments": False,
        "allow_indeterminate": False,
        "allow_other_option": False,
        "custom_design_colors": None,
        "deadline_at": None,
        "duplication_checking": "ip",
        "allow_vpn_users": False,
        "edit_vote_permissions": "nobody",
        "force_appearance": None,
        "hide_participants": True,
        "is_multiple_choice": True,
        "multiple_choice_min": 1,
        "multiple_choice_max": 5,
        "number_of_winners": 1,
        "randomize_options": False,
        "require_voter_names": False,
        "results_visibility": "always",
        "use_custom_design": False
    },
    "poll_meta": {
        "description": "Votación a peor canción de la lista de Spotify: " + playlist['name'],
        "location": None,
    },
    "type": "multiple_choice",
}

## CREATE THE POLL ##
responseWinner = requests.post(ENDPOINT + '/polls', json=payloadWinner,
                               headers={'X-API-KEY': POLL_API_KEY})
responseLoser = requests.post(ENDPOINT + '/polls', json=payloadLoser,
                              headers={'X-API-KEY': POLL_API_KEY})

# IF THE POLL WAS CREATED SUCCESSFULLY ##
# SEND MESSAGE TO THE CHAT ##
if responseWinner and responseLoser:
    pollWinner = responseWinner.json()  # response is Poll object
    pollLoser = responseLoser.json()  # response is Poll object

    myTeamsMessage = pymsteams.connectorcard(
        'https://udcgal.webhook.office.com/webhookb2/7d7f1a2f-ae0a-44e0-ac50-e00805868bd7@cea1ea3e-60b2-4f75-a6c2-a6022e8f961b/IncomingWebhook/98d219312d454e978519868e649628c3/cbb6d941-6bd7-4902-9aae-d20773571071')

    # Add color to the message
    myTeamsMessage.color('#e655bd')

    textTitle = '<h1 style="font-size:40px;color:#e655bd;text-align:center;" > &#11088 Día de votaciones! &#11088 </h1>'
    textTitleImg = '<div style="text-align:center;"> <img style="width:400px;" width="400" height="400" src="https://s1.dmcdn.net/v/SjEZa1W1UhkylYfrq/x1080"> </img> </div>'
    textDescription = "<h1 style='text-align:center;color:#e655bd'> <b> Están ustedes <del> cordialmente invitadxs</del> obligados a participar en la votación de la mejor/peor canción de esta semana. </b></h1>"
    textDescription2 = "<h1>Mediante este ejercicio por fin podremos determinar quienes son las personas con el mejor y peor gusto musical del laboratorio (nada mas y nada menos).</h1>"

    textDescription3 = "<h2> &#128077 Privilegios de los que gozará el ganador de la semana:</h2><ul><li>Podrá añadir una canción más a la lista esta semana</li><li>Regodearse de tener un gusto músical exquisito</li></ul></h2>"
    textDescription4 = "<h2> &#128078 Castigo para el perdedor de la semana:</h2><ul><li>Solo podrá añadir una canción a la lista, será su oportunidad para resarcirse</li><li>Poder decir al resto del grupo que no sirve de nada <q>echarle margaritas a los cerdos</q></li></ul></h2>"
    textDescription5 = "<h3>Los resultados de la encuesta saldrán el lunes con el informe semanal (o cuando el admin se acuerde de darle al botón) </h3>"

    textFooter = '<div style="text-align:center;"><a style="font-size:30px;" href="' + \
        pollWinner["url"] + '"> Mejor Canción</a><a style="font-size:30px;padding-left:50px" href="' + \
        pollLoser["url"] + '"> Peor Canción</a></div>'

    textFooterImg = '<div style="text-align:center;"> <img style="width:400px;" width="400" height="400" src="https://img.buzzfeed.com/buzzfeed-static/static/enhanced/terminal01/2011/4/28/16/enhanced-buzz-28256-1304022880-33.jpg"> </img> </div>'

    myTeamsMessage.title("")
    myTeamsMessage.text(
        '<div>' + textTitle + textTitleImg + '<br/>' + textDescription + '<br/>' + textDescription2 + '<br/>' + textDescription3 + '<br/>' + textDescription4 + '<br/>' + textDescription5 + '<br/>' + textFooter + '<br/>' + textFooterImg + '<div>')
    # Send the message.
    myTeamsMessage.send()

    # PERSIST FOR LATER THE URLS ##
    urls = {
        "urlWinner": pollWinner["url"],
        "urlLoser": pollLoser["url"]
    }
    afile = open('poll_id.pkl', 'wb')
    pickle.dump(urls, afile)
    afile.close()

else:
    errorWinner = responseWinner.json()
    errorLoser = responseLoser.json()
    print(errorWinner)
    print(errorLoser)
