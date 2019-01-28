'''decompressing the timd headers from super scout and putting them into a dictionary'''
#the values for the dictionary
SUPERVALUE = {
    'T': True,
    'F': False,
    'B': 'blue',
    'R': 'red',
    'G': 'orange',
    'L': 'lemon',
}
#the keys for the dictionary
SUPERKEY = {
    'a': 'cargoShipPreloads',
    'b': 'leftNear',
    'c': 'leftMid',
    'd': 'leftFar',
    'e': 'rightNear',
    'f': 'rightMid',
    'g': 'rightFar',
    'h': 'noShowTeams',
    'j': 'pathConflicts',
    'k': 'redScore',
    'm': 'blueScore',
    'n': 'redFoulPoints',
    'p': 'blueFoulPoints',
    'q': 'blueDidRocketRP',
    'r': 'redDidRocketRP',
    's': 'blueDidClimbRP',
    't': 'redDidClimbRP',
}
#an example of the compressed data we would get from the scouts
SCOUTEDDATA = 'S!Q1-B|a{bG;cL;dG;eL;fG;gL},h[1678],j1,k151,m127,n8,p4,qT,rF,sT,tF_1{u1678;v4;w1;x3;y2;z"Disabled, battery fell out";A8;B4},2{u254;v3;w2;x1;y3;z"Yellow card";A7;B5},3{u971;v1;w3;x2;y1;z"Fell down";A9;B6}'
#splitting the string to isolate the headers sections
INSIGNIFICANTSPLIT = SCOUTEDDATA.split('|')[1]
HEADER = INSIGNIFICANTSPLIT.split('_')[0]
HEADSUPER = HEADER.split(',')
#the dictiony that wll get filled in the end
DECOMPRESSEDSUPER = {}
#itterates through the headers and splits up the keys from the values
for item in HEADSUPER:
    key = item[0]
    value = item[1:]
    UNCOMPRESSSUPER = SUPERKEY[key]
#determines if the key is 'a'
#if the key is then it gets the dictionary after it
    if 'a' in item:
        PRELOADPIECES = item[2:-1]
        PRELOAD = [GAMEPIECE for GAMEPIECE in PRELOADPIECES.split(';')]
        CARGOSHIPPRELOAD = {}
#it itterates through the dictionsry to decompress the letters individually
        for compressed in PRELOAD:
            PIECEKEY = compressed[0]
            PIECEVALUE = compressed[1:]
            UNCOMPRESSEDPRELOAD = SUPERKEY[PIECEKEY]
#then it adds the smaller dictionary to the larger one
            CARGOSHIPPRELOAD[UNCOMPRESSEDPRELOAD] = SUPERVALUE[PIECEVALUE]
            DECOMPRESSEDSUPER[UNCOMPRESSSUPER] = CARGOSHIPPRELOAD
#this checks if the item starts with 'h'
#if it does then item is split into a list and is added to the dictionary
    if 'h' in item:
        TEAMS = item[2:-1]
        NOSHOW = [int(TEAMNUM) for TEAMNUM in TEAMS.split(';')]
        DECOMPRESSEDSUPER[UNCOMPRESSSUPER] = NOSHOW
#otherwise, if item is one letter then item will be added as a string
    elif len(value) == 1 and value.isalpha() is True:
        DECOMPRESSEDSUPER[UNCOMPRESSSUPER] = SUPERVALUE[value]
#otherwise, if item is a number then it is stored in the dictionary as a integer
    elif value.isdigit() is True:
        DECOMPRESSEDSUPER[UNCOMPRESSSUPER] = int(value)
#displays dictionary
print(DECOMPRESSEDSUPER)
