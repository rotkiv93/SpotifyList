import requests
import os
import pymongo
from bson.objectid import ObjectId
from dotenv import load_dotenv

load_dotenv()

ENDPOINT = "https://api.strawpoll.com/v3"
API_KEY = "YOUR_API_KEY"
MONGODB_URL = os.getenv('MONGO_DB_URL')

class Track():
    def __init__(self):
        self.track = None
        self.votes = None


class PollAnalytics:
    def __init__(self):
        self.pollWinner = None
        self.pollLoser = None


def getAllPollAnalytics():

    ## LOAD BOTH PERSISTED POLLS ##
    cliente = pymongo.MongoClient(MONGODB_URL)
    db = cliente.test
    res = db.get_collection("polls").find_one({"_id": ObjectId("630367dfc8fa5342204d59d2")})

    # Use "NPgxkzPqrn2" for an example without participants
    pollUrlWinner = res["pollWinners"].split('/')[-1]
    pollUrlLoser = res["pollLosers"].split('/')[-1]
    
    return {
        "pollWinner": getPollAnalytics(pollUrlWinner),
        "pollLoser": getPollAnalytics(pollUrlLoser)
    }


def getPollAnalytics(pollUrl):
    response = requests.get(ENDPOINT + '/polls/' + pollUrl +
                            '/results', headers={'X-API-KEY': API_KEY})

    Tracks = []
    participantCount = ''

    ## EXTRACT THE TRACKS FROM THE POLL ##
    if response:
        poll_results = response.json()  # response is PollResults object
        for option in poll_results["poll_options"]:
            newTrack = Track()
            newTrack.track = option["value"]
            newTrack.votes = option["vote_count"]
            Tracks.append(newTrack)

        participantCount = str(poll_results["participant_count"])

        ## SORT THE TRACKS BY VOTE COUNT ##
        Tracks.sort(key=lambda x: x.votes, reverse=True)
        return {
            "Tracks": Tracks,
            "participantCount": participantCount
        }

    else:
        error = response.json()
        print(error)
