def parseTrackName(trackName):
    parsedName = ""
    if (len(trackName.track.split(' - ')) > 2):
        parsedName = trackName.track.split(
            ' - ')[0] + ' - ' + trackName.track.split(' - ')[1]
    else:
        parsedName = trackName.track.split(' - ')[0]
    return parsedName


def getTopResults(list):
    topResults = []
    firstElem = list[0]
    for track in list:
        if (track.votes == firstElem.votes):
            topResults.append(track)

    return topResults
